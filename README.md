# Speed Estimation

This add-on calculates the speed of trackable objects based on their past and present coordinates in the frame. We implement the speed estimation algorithm proposed on the following paper:

<https://ieeexplore.ieee.org/document/6614066>


### Config

The class `SpeedEstimationProcessor` is initialized with the following config parameters. The majority of the below parameters rely on the tech specifications of the input camera,

```python
DEFAULT = {
    "person_action": True,
    "camera_length": 4.5,
    "fps": 30,
    "lens_dimension": 0,
    "focal_length": 0,
    "camera_horizontal_degrees": 80,
    "camera_vertical_degrees": 53
}
```

where:
- `person_aciton` (bool): Calculates the following actions for person detections - `walking | running | standing`
- `camera_length` (float | int): The maximum distance of the camera to the scene
- `fps` (int): Frames per second
- `lens_dimension` (int): The camera's lens dimension in millimeters. This value is optional if the `camera_horizontal_degrees` and `camera_vertical_degrees` are specified instead.
- `focal_length` (int): The camera's focal length in millimeters. The value is optional if the `camera_horizontal_degrees` and `camera_vertical_degrees` are specified instead. 
- `camera_horizontal_degrees` (int): The camera's horizontal view in degrees. The value is optional if the `lens_dimension` and `focal_length` are specified instead. 
- `camera_vertical_degrees` (int): The camera's vertical view in degrees. This value is optional if the `lens_dimension` and `focal_length` are specified instead.

If a custom set of config parameters is not provided add input, the add-on is initialized using the default parameteres shown above. 

### Input

The `post_process` gets as input the `AddonObject` and relies on the results of the `tracking` add-on set in:

- `AddonObject.shared['trackable_objects']` (format: `OrderedDict`)
- `AddonObject.shared['trackable_objects_history']` (format: `OrderedDict`)
- `AddonObject.frame.shape` (format: `frame_height, frame_width`)

**Direct dependency with the `tracking` add-on.**

### Process

After object detection and object tracking, the speed estimator receives the full history of `trackable_objects` from the `tracking` add-on. For every `trackable_object` we check its previous positions from the past frames and estimate the object's speed on the current frame.

If an object is not tracked on the current frame, (due to low confidence detection or the person has temporarily disappeared from the fov), we assume its speed to be the same as the one from the previous frame. This assumes a stable speed throughout time for the next time we get a new detection and position for that object.

When the flag `person_action`, we perform an additional processing step, where we calculate whether a person is 'walking | standing | running'. These actions are determined based on the assumption that the average running speed for a person is estimated around `9.1` kph and the average walking speed is `1.5` kph.


### Output

The add-on's output is shared on the `AddonObject.inference.extra` for each object that was actively tracked by the `tracking` add-on on the current frame:

- `AddonObject.inference.extra['current_speed']` - (format: `dict` where `{'obj_id': speed}`)
- `AddonObject.inference.extra['current_action']` - (format: `dict` where `{'obj_id': speed}`)

