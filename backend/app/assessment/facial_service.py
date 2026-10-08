from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms


# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "ml"
    / "models"
    / "facial_emotion_cnn_v2.pth"
)


# ------------------------------------------------------------
# Emotion classes
# ------------------------------------------------------------

EMOTION_CLASSES = [
    "angry",
    "disgust",
    "fear",
    "happy",
    "neutral",
    "sad",
    "surprise",
]


# ------------------------------------------------------------
# CNN architecture
# ------------------------------------------------------------

class FacialEmotionCNN(nn.Module):

    def __init__(self, num_classes=7):
        super().__init__()

        self.features = nn.Sequential(

            # Block 1
            nn.Conv2d(
                1,
                32,
                kernel_size=3,
                padding=1
            ),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),

            nn.Conv2d(
                32,
                32,
                kernel_size=3,
                padding=1
            ),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),

            nn.MaxPool2d(2),
            nn.Dropout2d(0.20),

            # Block 2
            nn.Conv2d(
                32,
                64,
                kernel_size=3,
                padding=1
            ),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),

            nn.Conv2d(
                64,
                64,
                kernel_size=3,
                padding=1
            ),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),

            nn.MaxPool2d(2),
            nn.Dropout2d(0.25),

            # Block 3
            nn.Conv2d(
                64,
                128,
                kernel_size=3,
                padding=1
            ),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),

            nn.Conv2d(
                128,
                128,
                kernel_size=3,
                padding=1
            ),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),

            nn.MaxPool2d(2),
            nn.Dropout2d(0.30),

            # Block 4
            nn.Conv2d(
                128,
                256,
                kernel_size=3,
                padding=1
            ),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),

            nn.MaxPool2d(2),
            nn.Dropout2d(0.35),
        )

        self.classifier = nn.Sequential(

            nn.Flatten(),

            nn.Linear(
                256 * 3 * 3,
                256
            ),

            nn.ReLU(inplace=True),

            nn.Dropout(0.5),

            nn.Linear(
                256,
                num_classes
            )
        )

    def forward(self, x):

        x = self.features(x)

        x = self.classifier(x)

        return x


# ------------------------------------------------------------
# Load model
# ------------------------------------------------------------

device = torch.device("cpu")

model = FacialEmotionCNN(
    num_classes=len(EMOTION_CLASSES)
).to(device)


checkpoint = torch.load(
    MODEL_PATH,
    map_location=device
)


model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()


# ------------------------------------------------------------
# OpenCV face detector
# ------------------------------------------------------------

FACE_CASCADE_PATH = (
    cv2.data.haarcascades
    + "haarcascade_frontalface_default.xml"
)

face_detector = cv2.CascadeClassifier(
    FACE_CASCADE_PATH
)

if face_detector.empty():
    raise RuntimeError(
        "Failed to load OpenCV Haar Cascade face detector."
    )


# ------------------------------------------------------------
# Image preprocessing
# ------------------------------------------------------------

image_transform = transforms.Compose([

    transforms.Grayscale(
        num_output_channels=1
    ),

    transforms.Resize(
        (48, 48)
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.5],
        std=[0.5]
    ),
])


# ------------------------------------------------------------
# Detect and crop face
# ------------------------------------------------------------

def detect_and_crop_face(image):
    """
    Detect the largest face in the image and return
    a cropped PIL image.

    The original image is not saved.
    """

    # Make sure the image is RGB
    image = image.convert("RGB")

    # PIL -> NumPy
    image_array = np.array(image)

    # RGB -> BGR for OpenCV
    image_bgr = cv2.cvtColor(
        image_array,
        cv2.COLOR_RGB2BGR
    )

    # Convert to grayscale
    gray = cv2.cvtColor(
        image_bgr,
        cv2.COLOR_BGR2GRAY
    )

    # Detect faces
    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80)
    )

    # No face detected
    if len(faces) == 0:

        print(
            "📷 No face detected in the captured image."
        )

        raise ValueError(
            "No face detected. Please make sure your face "
            "is clearly visible and facing the camera."
        )

    # --------------------------------------------------------
    # Select the largest detected face
    # --------------------------------------------------------

    largest_face = max(
        faces,
        key=lambda face: face[2] * face[3]
    )

    # Debug information
    print(
        f"📷 Faces detected: {len(faces)} | "
        f"Selected face: {largest_face}"
    )

    x, y, width, height = largest_face

    # --------------------------------------------------------
    # Add padding around the face
    # --------------------------------------------------------

    padding_x = int(width * 0.20)
    padding_y = int(height * 0.20)

    image_height, image_width = gray.shape

    x1 = max(
        0,
        x - padding_x
    )

    y1 = max(
        0,
        y - padding_y
    )

    x2 = min(
        image_width,
        x + width + padding_x
    )

    y2 = min(
        image_height,
        y + height + padding_y
    )

    # --------------------------------------------------------
    # Crop face
    # --------------------------------------------------------

    face_crop = image.crop(
        (x1, y1, x2, y2)
    )

    print(
        f"📷 Face crop: "
        f"x={x1}, y={y1}, "
        f"width={x2 - x1}, "
        f"height={y2 - y1}"
    )

    return face_crop


# ------------------------------------------------------------
# Predict facial emotion
# ------------------------------------------------------------

def predict_facial_emotion(image):

    if image is None:

        raise ValueError(
            "No facial image was provided."
        )

    # Open uploaded image
    if not isinstance(image, Image.Image):

        image = Image.open(image)

    # --------------------------------------------------------
    # Detect and crop face
    # --------------------------------------------------------

    face_crop = detect_and_crop_face(
        image
    )

    # --------------------------------------------------------
    # Prepare image for CNN
    # --------------------------------------------------------

    tensor = image_transform(
        face_crop
    ).unsqueeze(0).to(device)

    # --------------------------------------------------------
    # CNN prediction
    # --------------------------------------------------------

    with torch.no_grad():

        outputs = model(
            tensor
        )

        probabilities = torch.softmax(
            outputs,
            dim=1
        )[0]

        predicted_index = torch.argmax(
            probabilities
        ).item()

        confidence = float(
            probabilities[predicted_index]
        )

    emotion = EMOTION_CLASSES[
        predicted_index
    ]

    # --------------------------------------------------------
    # Debug output
    # --------------------------------------------------------

    print(
        f"📷 Facial emotion detected: {emotion}"
    )

    print(
        f"📷 Facial confidence: {confidence:.4f}"
    )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {
        "emotion": emotion,
        "confidence": confidence,
    }