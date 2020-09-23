import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM
import tensorflow_hub as hub
import tensorflow_datasets as tfds
import numpy as np
from openpyxl import load_workbook
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
        for i in range(len(train_change)):
            if train_change[i] > 0:
                train_change[i] = 1
            else:
                train_change[i] = 0

        self.labels = np.array(train_change)
        print(self.labels)
        self.embed = hub.load(
            "https://tfhub.dev/google/nnlm-en-dim128-with-normalization/2")
        self.embeddings = self.embed(self.data)
        # print(embeddings[0])
        self.embeddings = tf.reshape(
            self.embeddings, [self.embeddings.shape[0], 128, 1])
        print(self.embeddings.shape[1:])
        # shuffle data - split data into validation set - reshuffle each iteration
        train_data = tf.data.Dataset.from_tensor_slices(
            (self.embeddings, self.labels))
        train_data = train_data.shuffle(
            len(self.labels), reshuffle_each_iteration=False)
        split = int(len(self.labels)*3/4)
        val_data = train_data.skip(split)
        train_data = train_data.take(split)
        train_data = train_data.shuffle(split, reshuffle_each_iteration=True)
        val_data = val_data.shuffle(
            len(self.labels)-split, reshuffle_each_iteration=True)

        self.model = Sequential()

        self.model.add(LSTM(128, input_shape=(
            self.embeddings.shape[1:]), return_sequences=True))
        self.model.add(Dropout(0.2))

        self.model.add(LSTM(128))
        self.model.add(Dropout(0.1))

        self.model.add(Dense(32, activation='relu'))
        self.model.add(Dropout(0.2))

        self.model.add(Dense(1))

        self.model.summary()

        self.model.compile(optimizer='adam',
                           loss=tf.keras.losses.BinaryCrossentropy(
                               from_logits=True),
                           metrics=['accuracy'])
        self.mod_weights = self.model.get_weights()
        self.greatest = 0.0
        for i in range(3):
            EPOCHS = 1000
            early_stop = keras.callbacks.EarlyStopping(
                monitor='val_loss', patience=10)

            history = self.model.fit(train_data.batch(20), epochs=EPOCHS, validation_data=val_data.batch(20),
                                     verbose=1, callbacks=[early_stop])

            results = self.model.evaluate(val_data.batch(20), verbose=2)
            if results[1] > self.greatest:
                self.greatest = results[1]
                self.saved_model = self.model
                # self.model.save('bimodel.h5')
            self.model.set_weights(self.mod_weights)
            print('Trial: ' + str(i))

    def retrain(self, new_dates, new_arts):
        # add new changes to labels
        print('Num new arts: ' + str(len(new_dates)))

        next_dates = []
        for i in range(len(new_dates)):
            if float(self.changes[str(NextDay(str(new_dates[i])).getNext())]) > 0:
                next_dates.append(1)
            else:
                next_dates.append(0)
            # next_dates.append(
            #     float(self.changes[str(NextDay(str(new_dates[i])).getNext())]))
        self.labels = np.append(self.labels, next_dates)

        # add new articles to data
        new_embeddings = self.embed(new_arts)
        new_embeddings = tf.reshape(
            new_embeddings, [new_embeddings.shape[0], 128, 1])
        self.embeddings = np.append(self.embeddings, new_embeddings)

        # shuffle data - split data into validation set - reshuffle each iteration
        train_data = tf.data.Dataset.from_tensor_slices(
            (self.embeddings, self.labels))
        train_data = train_data.shuffle(
            len(self.labels), reshuffle_each_iteration=False)
        split = int(len(self.labels)*3/4)
        val_data = train_data.skip(split)
        train_data = train_data.take(split)
        train_data = train_data.shuffle(split, reshuffle_each_iteration=True)
        val_data = val_data.shuffle(
            len(self.labels)-split, reshuffle_each_iteration=True)

        for i in range(3):
            EPOCHS = 1000
            early_stop = keras.callbacks.EarlyStopping(
                monitor='val_loss', patience=10)

            history = self.model.fit(train_data.batch(128), epochs=EPOCHS, validation_data=val_data.batch(128),
                                     verbose=0, callbacks=[early_stop, tfdocs.modeling.EpochDots()])

            results = self.model.evaluate(val_data.batch(20), verbose=2)
            if results[1] > self.greatest:
                self.greatest = results[1]
                self.saved_model = self.model
                # self.model.save('bimodel.h5')
            self.model.set_weights(self.mod_weights)
            print('Trial: ' + str(i))
        print('Number of Articles: ' + str(len(self.labels)))

    def predict(self, arts):
        preds = []
        for i in range(len(arts)):
            preds.append(float(self.saved_model.predict([arts[i]])))
        return np.array(preds)
