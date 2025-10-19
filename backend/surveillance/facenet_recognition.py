"""
FaceNet + MTCNN Face Recognition Module
Modern face detection and recognition for authorized/unknown persons
"""

import numpy as np
from mtcnn import MTCNN
from keras.models import load_model
import cv2
import os
from numpy import asarray, expand_dims
from sklearn.preprocessing import Normalizer
from sklearn.metrics.pairwise import cosine_similarity

class FaceNetRecognizer:
    def __init__(self, known_faces_dir="data/known_faces", model_path="facenet_keras.h5"):
        self.known_faces_dir = known_faces_dir
        self.detector = MTCNN()
        self.model = load_model(model_path)
        self.in_encoder = Normalizer(norm='l2')
        self.embeddings = []
        self.names = []
        self.load_known_faces()

    def extract_face(self, filename, required_size=(160, 160)):
        image = cv2.imread(filename)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.detector.detect_faces(image)
        if len(results) == 0:
            return None
        x1, y1, width, height = results[0]['box']
        x1, y1 = max(x1, 0), max(y1, 0)
        x2, y2 = x1 + width, y1 + height
        face = image[y1:y2, x1:x2]
        face = cv2.resize(face, required_size)
        return face

    def get_embedding(self, face_pixels):
        face_pixels = face_pixels.astype('float32')
        mean, std = face_pixels.mean(), face_pixels.std()
        face_pixels = (face_pixels - mean) / std
        samples = expand_dims(face_pixels, axis=0)
        yhat = self.model.predict(samples)
        return yhat[0]

    def load_known_faces(self):
        self.embeddings = []
        self.names = []
        for person_name in os.listdir(self.known_faces_dir):
            person_dir = os.path.join(self.known_faces_dir, person_name)
            if not os.path.isdir(person_dir):
                continue
            for filename in os.listdir(person_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    path = os.path.join(person_dir, filename)
                    face = self.extract_face(path)
                    if face is not None:
                        embedding = self.get_embedding(face)
                        self.embeddings.append(embedding)
                        self.names.append(person_name)

    def recognize(self, image):
        faces = self.detector.detect_faces(image)
        results = []
        for face in faces:
            x1, y1, width, height = face['box']
            x1, y1 = max(x1, 0), max(y1, 0)
            x2, y2 = x1 + width, y1 + height
            face_img = image[y1:y2, x1:x2]
            face_img = cv2.resize(face_img, (160, 160))
            embedding = self.get_embedding(face_img)
            embedding = self.in_encoder.transform([embedding])[0]
            scores = cosine_similarity([embedding], self.embeddings)[0]
            best_idx = np.argmax(scores)
            best_score = scores[best_idx]
            name = self.names[best_idx] if best_score > 0.5 else "unknown"
            results.append({
                'box': face['box'],
                'name': name,
                'score': float(best_score)
            })
        return results

if __name__ == "__main__":
    # Example usage
    recognizer = FaceNetRecognizer(known_faces_dir="backend/data/known_faces", model_path="facenet_keras.h5")
    img = cv2.imread("test.jpg")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = recognizer.recognize(img)
    print(results)
