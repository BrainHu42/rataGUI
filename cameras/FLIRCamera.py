from .BaseCamera import BaseCamera

import cv2

try:
    import PySpin
    FLIR_DETECTED = True
except ImportError as e:
    print('PySpin module not detected')
    FLIR_DETECTED = False


class FLIRCamera(BaseCamera):

    CameraProperties = {
        "LineSelector" : PySpin.LineSelector_Line2,
        "LineMode" : PySpin.LineMode_Output,
        "LineSource": PySpin.LineSource_ExposureActive,
        "AcquisitionFrameRateEnable": True,
        "AcquisitionFrameRate" : 30,
    }

    # EasySpinProperties = ["AcquisitionFrameRate",]

    # Global pyspin system variable
    _SYSTEM = None

    @staticmethod
    def getCameraList():
        '''Return a list of Spinnaker cameras that must be cleared. Also initializes the PySpin 'System', if needed.'''

        if FLIRCamera._SYSTEM is None:
            FLIRCamera._SYSTEM = PySpin.System.GetInstance()
        else:
            FLIRCamera._SYSTEM.UpdateCameras()
    
        return FLIRCamera._SYSTEM.GetCameras()

    @staticmethod
    def getAllCameras():
        '''Returns dictionary of all available FLIR cameras'''
        cameras = {}
        cam_list = FLIRCamera.getCameraList()
        for cam in cam_list:
            # print(camera.TLDevice.DeviceSerialNumber.ToString())
            if cam.TLDevice.DeviceSerialNumber.GetAccessMode() == PySpin.RO:
                serial_number = cam.TLDevice.DeviceSerialNumber.ToString()
                # Create camera wrapper object
                cameras[serial_number] = FLIRCamera(serial_number)
        cam_list.Clear()
        return cameras

    def __init__(self, cameraID: str):

        super().__init__()
        self.cameraID = cameraID
        self._initialized = False
        self.last_frame = None
        self.last_index = 0

    def configure_chunk_data(self, nodemap, selected_chucks, enable = True) -> bool:
        """
        Configures the camera to add chunk data to each image.

        :param nodemap: Transport layer device nodemap.
        :type nodemap: INodeMap
        :return: True if successful, False otherwise
        :rtype: bool
        """
        try:
            result = True

            # Activate chunk mode
            # Once enabled, chunk data will be available at the end of the payload of every image captured until it is disabled.
            chunk_mode_active = PySpin.CBooleanPtr(nodemap.GetNode('ChunkModeActive'))

            if PySpin.IsAvailable(chunk_mode_active) and PySpin.IsWritable(chunk_mode_active):
                chunk_mode_active.SetValue(True)

            chunk_selector = PySpin.CEnumerationPtr(nodemap.GetNode('ChunkSelector'))

            if not PySpin.IsAvailable(chunk_selector) or not PySpin.IsReadable(chunk_selector):
                print('Unable to retrieve chunk selector. Aborting...\n')
                return False

            # Retrieve entries from enumeration ptr
            entries = [PySpin.CEnumEntryPtr(chunk_selector_entry) for chunk_selector_entry in chunk_selector.GetEntries()]

            # Select entry nodes to enable
            for chunk_selector_entry in entries:
                # Go to next node if problem occurs
                if not PySpin.IsAvailable(chunk_selector_entry) or not PySpin.IsReadable(chunk_selector_entry):
                    result = False
                    continue

                chunk_str = chunk_selector_entry.GetSymbolic()

                if chunk_str in selected_chucks:
                    chunk_selector.SetIntValue(chunk_selector_entry.GetValue())

                    # Retrieve corresponding boolean
                    chunk_enable = PySpin.CBooleanPtr(nodemap.GetNode('ChunkEnable'))

                    # Enable the corresponding chunk data
                    if enable:
                        if chunk_enable.GetValue() is True:
                            print('{} enabled'.format(chunk_str))
                        elif PySpin.IsWritable(chunk_enable):
                            chunk_enable.SetValue(True)
                            print('{} enabled'.format(chunk_str))
                        else:
                            print('{} not writable'.format(chunk_str))
                            result = False
                    else:
                        # Disable the boolean, thus disabling the corresponding chunk data
                        if PySpin.IsWritable(chunk_enable):
                            chunk_enable.SetValue(False)
                        else:
                            result = False

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        return result

    def initializeCamera(self, prop_dict: dict = {}, drop_frames = True) -> bool:
        self._running = False
        cam_list = FLIRCamera.getCameraList()

        if cam_list.GetSize() == 0:
            print("No camera available")
            cam_list.Clear()
            return False
        
        self.stream = cam_list.GetBySerial(self.cameraID)
        cam_list.Clear()

        # Initialize stream
        if not self.stream.IsInitialized():
            self.stream.Init()

        nodemap = self.stream.GetNodeMap()
        enabled_chunks = ["FrameID", "Timestamp"] # ExposureTime, PixelFormat
        self.configure_chunk_data(nodemap, enabled_chunks)

        if drop_frames:
            self.stream.TLStream.StreamBufferHandlingMode.SetValue(PySpin.StreamBufferHandlingMode_NewestOnly)
        else:
            self.stream.TLStream.StreamBufferHandlingMode.SetValue(PySpin.StreamBufferHandlingMode_NewestFirst)

        for prop_name, value in prop_dict.items():
            try: 
                node = getattr(self.stream, prop_name)
                node.SetValue(value)
            except Exception as err:
                print(err)
                return False
        self.initialized = True
        self.startStream()

        return True

    def startStream(self):
        self.stream.BeginAcquisition()
        self._running = True

    def endStream(self):
        self.stream.EndAcquisition()
        self._running = False

    def readCamera(self, colorspace="BGR"):
        if not self._running:
            return False, None

        img_data = self.stream.GetNextImage()
        if img_data.IsIncomplete():
            print('Image incomplete with image status %d ...' % img_data.GetImageStatus())
            img_data.Release()
            return False, None

        # Parse image metadata
        chunk_data = img_data.GetChunkData()
        new_index = chunk_data.GetFrameID()

        if self.last_frame is not None:
            dropped = new_index - self.last_index - 1
            if dropped > 0:
                print(f"Dropped {dropped} Frame(s)")

        self.last_index = new_index

        frame = img_data.GetNDArray()
        match colorspace:
            case "BGR":
                self.last_frame = cv2.cvtColor(frame, cv2.COLOR_BayerBG2BGR)
            case "RGB":
                self.last_frame = cv2.cvtColor(frame, cv2.COLOR_BayerBG2RGB)
            case "GRAY":
                self.last_frame = cv2.cvtColor(frame, cv2.COLOR_BayerBG2GRAY)

        # Release image from camera buffer
        img_data.Release()
        return True, self.last_frame

    def stopCamera(self):
        if self.stream is not None:
            if self.stream.IsStreaming():
                self.stream.EndAcquisition()
            
            self.stream.DeInit()
            del self.stream

        self._initialized = False
        self._running = False

    def getCameraID(self):
        return self.cameraID

    def isOpened(self):
        return self._running


# EnumerationCount - Camera_EnumerationCount_get(self)
# TransferQueueOverflowCount
# GetCounterValue