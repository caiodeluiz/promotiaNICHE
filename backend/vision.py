from google.cloud import vision
import os

def detect_labels(image_path: str) -> list[str]:
    """Detects labels in the file."""
    # If credentials are not set, return dummy data for development
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("Warning: GOOGLE_APPLICATION_CREDENTIALS not set. Returning dummy labels.")
        return ["yoga", "mat", "exercise", "purple", "fitness"]

    client = vision.ImageAnnotatorClient()

    with open(image_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.label_detection(image=image)
    labels = response.label_annotations

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(
                response.error.message
            )
        )

    return [label.description.lower() for label in labels]
