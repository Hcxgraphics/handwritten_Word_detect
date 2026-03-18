from pathlib import Path
import cv2
import layoutparser as lp

# class LayoutDetector:
#     def __init__(self, config):
#         # Access use_gpu as: config["device"]["use_gpu"]
#         use_gpu = config["device"]["use_gpu"]  # <--- extract this safely
        
#         self.model = lp.Detectron2LayoutModel(
#             config["layout"]["model_config"],
#             extra_config=[
#                 "MODEL.ROI_HEADS.SCORE_THRESH_TEST",
#                 config["layout"]["score_thresh"]
#             ],
#             device="cuda" if use_gpu else "cpu"
#         )

import layoutparser as lp

class LayoutDetector:
    def __init__(self, config):
        use_gpu = config["device"]["use_gpu"]  # get from your config.yaml
        model_config = Path(config["layout"]["model_config"])
        if not model_config.is_absolute():
            model_config = Path(__file__).resolve().parents[2] / model_config

        self.model = lp.Detectron2LayoutModel(
            config_path=str(model_config),
            label_map={0: "Table", 1: "Text"},
            extra_config=[
                "MODEL.ROI_HEADS.SCORE_THRESH_TEST", config["layout"]["score_thresh"]
            ],
            device="cuda" if use_gpu else "cpu"
        )

    def detect_blocks(self, img_rgb):
        return self.model.detect(img_rgb)


