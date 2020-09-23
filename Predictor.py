import tensorflow as tf
from tensorflow import keras
from keras import layers
import tensorflow_docs as tfdocs
import tensorflow_docs.plots
import tensorflow_docs.modeling
import tensorflow_hub as hub
import tensorflow_datasets as tfds
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import openpyxl as xl


class Predictor():
    def __init__(self):
        self.model = tf.keras.models.load_model(
            'bimodel.h5', custom_objects={'KerasLayer': hub.KerasLayer})

    def predict(self, arts):
        self.articles = np.array(arts)
        prediction = self.model.predict(self.articles)
        return prediction
