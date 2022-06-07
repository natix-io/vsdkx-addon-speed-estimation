import numpy as np
import unittest

from vsdkx.core.structs import AddonObject, Inference
from vsdkx.addon.speed_estimation.processor import SpeedEstimationProcessor
from vsdkx.addon.tracking.trackableobject import TrackableObject


class TestAddon(unittest.TestCase):
    addon_config = {
        "person_action": False,
        "camera_length": 4.5,
        "fps": 30,
        "lens_dimension": 0,
        "focal_length": 1,
        "camera_horizontal_degrees": 80,
        "camera_vertical_degrees": 53
    }

    model_config = {
        "filter_class_ids": [0]
    }

    def test_get_movement_action(self):
        addon_processor = SpeedEstimationProcessor(self.addon_config, {}, self.model_config, {})

        running_action = addon_processor._get_movement_action(10)
        walking_action = addon_processor._get_movement_action(5)
        standing_action = addon_processor._get_movement_action(1)

        standing_action_2 = addon_processor._get_movement_action(-10)

        self.assertEqual(running_action, 'running')
        self.assertEqual(walking_action, 'walking')
        self.assertEqual(standing_action, 'standing')

        self.assertEqual(standing_action_2, 'standing')

    def test_get_object_speed(self):
        addon_processor = SpeedEstimationProcessor(self.addon_config, {}, self.model_config, {})

        frame = (np.random.rand(640, 640, 3) * 100).astype('uint8')
        bb_1 = np.array([120, 150, 170, 200])
        c_1 = (145, 175)

        trackable_object_1 = TrackableObject(0, c_1, bb_1)
        trackable_object_2 = TrackableObject(1, c_1, bb_1)
        trackable_object_2.centroids.extend([c_1, c_1])

        trackable_object_3 = TrackableObject(2, c_1, bb_1)
        trackable_object_3.centroids.extend([c_1, c_1])
        trackable_object_3.speeds = [0] * (self.addon_config['fps'] + 1)

        shared = {
            "trackable_objects": {
                "0": trackable_object_1,
                "1": trackable_object_2,
                "2": trackable_object_3
            },
            "trackable_objects_history": {
                "0": trackable_object_1,
                "1": trackable_object_2,
                "2": trackable_object_3
            }
        }

        addon_processor._get_object_speed(shared.get('trackable_objects', {}), frame.shape[0], frame.shape[1])

        self.assertEqual(trackable_object_1.current_speed, 0)
        self.assertEqual(len(trackable_object_1.speeds), 1)

        self.assertEqual(trackable_object_2.current_speed, 0)
        self.assertEqual(len(trackable_object_2.speeds), 1)

        self.assertEqual(trackable_object_3.current_speed, 0)
        self.assertEqual(len(trackable_object_3.speeds), self.addon_config['fps'] + 2)

        new_config = self.addon_config.copy()
        new_config['person_action'] = True
        new_config['camera_horizontal_degrees'] = 0
        new_config['camera_vertical_degrees'] = 0
        addon_processor = SpeedEstimationProcessor(new_config, {}, self.model_config, {})

        addon_processor._get_object_speed(shared.get('trackable_objects', {}), frame.shape[0], frame.shape[1])

        self.assertEqual(trackable_object_1.action, "")
        self.assertNotEqual(trackable_object_2.action, "")
        self.assertNotEqual(trackable_object_3.action, "")

    def test_post_process(self):
        addon_processor = SpeedEstimationProcessor(self.addon_config, {}, self.model_config, {})

        frame = (np.random.rand(640, 640, 3) * 100).astype('uint8')
        inference = Inference()

        bb_1 = np.array([120, 150, 170, 200])
        c_1 = (145, 175)

        trackable_object_1 = TrackableObject(0, c_1, bb_1)
        trackable_object_1.centroids.extend([c_1, c_1])

        shared = {
            "trackable_objects": {
                "0": trackable_object_1,
            },
            "trackable_objects_history": {
                "0": trackable_object_1,
            }
        }

        test_object = AddonObject(frame=frame, inference=inference, shared=shared)
        result = addon_processor.post_process(test_object)

        self.assertIn('current_speed', result.inference.extra)
        self.assertNotIn('current_action', result.inference.extra)
        self.assertIn('0', result.inference.extra['current_speed'])

        self.addon_config['person_action'] = True
        addon_processor = SpeedEstimationProcessor(self.addon_config, {}, self.model_config, {})
        result = addon_processor.post_process(test_object)

        self.assertIn('current_action', result.inference.extra)
        self.assertIn('0', result.inference.extra['current_action'])


if __name__ == '__main__':
    unittest.main()
