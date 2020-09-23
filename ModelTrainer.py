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
from openpyxl import load_workbook
import csv
from NextDay import NextDay


class ModelTrainer():
    def __init__(self, dates, articles):
        labels = []
        self.data = np.array(articles)

        # change dates to next date stock market was open
        for day in dates:
            labels.append(str(NextDay(day).getNext()))
        self.labels = np.array(labels)

        # load the stock changes
        stockws = load_workbook('NVDA\\NVDA.xlsx', data_only=True).active
        self.changes = {}
        for row in stockws.rows:
            self.changes[str(row[0].value)] = str(row[1].value)

        # create an array of changes for the day after the article was published
        train_change = []
        for ind in range(len(self.data)):
            train_change.append(float(float(self.changes[self.labels[ind]])))
        self.labels = np.array(train_change)

        # shuffle data - split data into validation set - reshuffle each iteration
        train_data = tf.data.Dataset.from_tensor_slices(
            (self.data, self.labels))
        train_data = train_data.shuffle(
            len(self.labels), reshuffle_each_iteration=False)
        split = int(len(self.labels)*3/4)
        val_data = train_data.skip(split)
        train_data = train_data.take(split)
        train_data = train_data.shuffle(split, reshuffle_each_iteration=True)
        val_data = val_data.shuffle(
            len(self.labels)-split, reshuffle_each_iteration=True)

        embedding = "https://tfhub.dev/google/tf2-preview/gnews-swivel-20dim/1"
        hub_layer = hub.KerasLayer(embedding, input_shape=[],
                                   dtype=tf.string, trainable=True)

        self.model = tf.keras.Sequential()
        self.model.add(hub_layer)
        self.model.add(tf.keras.layers.Dense(20, activation='relu'))
        self.model.add(tf.keras.layers.Dense(1))

        self.model.summary()

        self.model.compile(loss='mse', optimizer=tf.keras.optimizers.RMSprop(0.001),
                           metrics=['mae', 'mse'])

        self.mod_weights = self.model.get_weights()
        lowest = 999.99
        for i in range(3):
            EPOCHS = 1000
            early_stop = keras.callbacks.EarlyStopping(
                monitor='val_mae', patience=2)

            history = self.model.fit(train_data.batch(20), epochs=EPOCHS, validation_data=val_data.batch(20),
                                     verbose=1, callbacks=[early_stop, tfdocs.modeling.EpochDots()])

            loss, mae, mse = self.model.evaluate(val_data.batch(20), verbose=2)
            print("Testing set Mean Abs Error: {:5.2f}%".format(mae))
            if float(mae) < lowest:
                lowest = float(mae)
                self.model.save("model.h5")
            self.model.set_weights(self.mod_weights)
            print('Trial: ' + str(i))
        self.lowest = lowest

    def getMAE(self):
        return self.lowest

    def retrain(self, new_dates, new_arts):
        # add new changes to labels
        print('Num new arts: ' + str(len(new_dates)))

        next_dates = []
        for i in range(len(new_dates)):
            next_dates.append(
                float(self.changes[str(NextDay(str(new_dates[i])).getNext())]))
        self.labels = np.append(self.labels, next_dates)

        # add new articles to data
        self.data = np.append(self.data, new_arts)

        # shuffle data - split data into validation set - reshuffle each iteration
        train_data = tf.data.Dataset.from_tensor_slices(
            (self.data, self.labels))
        train_data = train_data.shuffle(
            len(self.labels), reshuffle_each_iteration=False)
        split = int(len(self.labels)*3/4)
        val_data = train_data.skip(split)
        train_data = train_data.take(split)
        train_data = train_data.shuffle(split, reshuffle_each_iteration=True)
        val_data = val_data.shuffle(
            len(self.labels)-split, reshuffle_each_iteration=True)

        lowest = 999.99
        for i in range(3):
            EPOCHS = 1000
            early_stop = keras.callbacks.EarlyStopping(
                monitor='val_mae', patience=2)

            history = self.model.fit(train_data.batch(20), epochs=EPOCHS, validation_data=val_data.batch(20),
                                     verbose=0, callbacks=[early_stop, tfdocs.modeling.EpochDots()])

            loss, mae, mse = self.model.evaluate(val_data.batch(20), verbose=2)
            print("Testing set Mean Abs Error: {:5.2f}%".format(mae))
            if float(mae) < lowest:
                lowest = float(mae)
                self.model.save("model.h5")
            self.model.set_weights(self.mod_weights)
            print('Trial: ' + str(i))
        self.lowest = lowest
        print('Number of Articles: ' + str(len(self.labels)))
