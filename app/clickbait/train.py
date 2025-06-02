# Importing libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from mlxtend.plotting import plot_confusion_matrix

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout, GlobalMaxPooling1D
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import joblib

# Define clickbait words for additional analysis
CLICKBAIT_WORDS = ['shocking', 'wow', 'unbelievable', 'amazing',
                   'you won\'t believe', 'mind-blowing', 'outrageous',
                   'secret', 'never seen before', 'warning', 'urgent',
                   'conspiracy', 'exposed', 'miracle', 'this is why',
                   'banned', 'controversial', 'breaking', 'things', 'NOT']


def preprocess_text(text):
    """Clean and normalize text data"""
    if not isinstance(text, str):
        return ""

    # Convert to lowercase
    text = text.lower()
    # Remove special characters and extra whitespace
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def load_and_prepare_data():
    """Load and prepare clickbait dataset"""
    # Load dataset - adjust path as needed
    FILE_PATH = 'clickbait_data.csv'  # Update this path to your dataset location
    try:
        data = pd.read_csv(FILE_PATH)
        print(f"Dataset loaded successfully with {len(data)} entries")
    except FileNotFoundError:
        print(f"Dataset not found at {FILE_PATH}")
        return None

    # Ensure dataset has required columns
    required_columns = ['headline', 'clickbait']
    if not all(col in data.columns for col in required_columns):
        print(f"Dataset missing required columns: {required_columns}")
        return None

    return data


def train_clickbait_model():
    """Train and evaluate the clickbait detection model using LSTM"""
    # Load and prepare data
    data = load_and_prepare_data()
    if data is None:
        return None, None

    # Parameters
    vocab_size = 5000
    maxlen = 500
    embedding_size = 32

    # Prepare features and target
    text = data['headline'].values
    labels = data['clickbait'].values

    # Split data
    text_train, text_test, y_train, y_test = train_test_split(text, labels)
    print(text_train.shape, text_test.shape, y_train.shape, y_test.shape)

    # Tokenize text
    tokenizer = Tokenizer(num_words=vocab_size)
    tokenizer.fit_on_texts(text)

    # Convert text to sequences
    X_train = tokenizer.texts_to_sequences(text_train)
    x_test = tokenizer.texts_to_sequences(text_test)

    # Pad sequences
    X_train = pad_sequences(X_train, maxlen=maxlen)
    x_test = pad_sequences(x_test, maxlen=maxlen)

    # Define LSTM model
    model = Sequential()
    model.add(Embedding(vocab_size, embedding_size, input_length=maxlen))
    model.add(LSTM(32, return_sequences=True))
    model.add(GlobalMaxPooling1D())
    model.add(Dropout(0.2))
    model.add(Dense(1, activation='sigmoid'))

    # Display model summary
    model.summary()

    # Define callbacks
    callbacks = [
        EarlyStopping(
            monitor='val_accuracy',
            min_delta=1e-4,
            patience=3,
            verbose=1
        ),
        ModelCheckpoint(
            filepath='model.weights.h5',
            monitor='val_accuracy',
            mode='max',
            save_best_only=True,
            save_weights_only=True,
            verbose=1,
            initial_value_threshold=0.0
        )
    ]

    # Compile and train model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    history = model.fit(
        X_train, y_train,
        batch_size=512,
        validation_data=(x_test, y_test),
        epochs=20,
        callbacks=callbacks
    )

    # Load best weights and save model
    model.load_weights('model.weights.h5')
    model.save('clickbait_model.h5')

    # Save tokenizer for predictions
    joblib.dump(tokenizer, 'tokenizer.pkl')

    # Plot training metrics
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']
    x = range(1, len(acc) + 1)

    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(x, acc, 'b', label='Training acc')
    plt.plot(x, val_acc, 'r', label='Validation acc')
    plt.title('Training and validation accuracy')
    plt.legend()
    plt.subplot(1, 2, 2)
    plt.plot(x, loss, 'b', label='Training loss')
    plt.plot(x, val_loss, 'r', label='Validation loss')
    plt.title('Training and validation loss')
    plt.legend()
    plt.show()

    # Plot confusion matrix
    preds = [round(i[0]) for i in model.predict(x_test)]
    cm = confusion_matrix(y_test, preds)
    plt.figure()
    plot_confusion_matrix(cm, figsize=(12, 8), hide_ticks=True, cmap=plt.cm.Blues)
    plt.xticks(range(2), ['Not clickbait', 'Clickbait'], fontsize=16)
    plt.yticks(range(2), ['Not clickbait', 'Clickbait'], fontsize=16)
    plt.show()

    # Calculate metrics
    tn, fp, fn, tp = cm.ravel()
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)

    print("Recall of the model is {:.2f}".format(recall))
    print("Precision of the model is {:.2f}".format(precision))

    return model, tokenizer


def predict_clickbait(model, tokenizer, headline, maxlen=500):
    """Predict if a headline is clickbait"""
    # Clean the headline
    clean_headline = preprocess_text(headline)

    # Convert to sequence and pad
    token_text = pad_sequences(tokenizer.texts_to_sequences([clean_headline]), maxlen=maxlen)

    # Make prediction
    probability = model.predict(token_text)[0][0]
    prediction = round(probability)

    # Find clickbait words
    clickbait_words_found = [word for word in CLICKBAIT_WORDS
                             if word.lower() in clean_headline.lower()]

    return {
        'is_clickbait': bool(prediction),
        'probability': float(probability),
        'clickbait_words': clickbait_words_found
    }


if __name__ == "__main__":
    model, tokenizer = train_clickbait_model()

    if model is not None and tokenizer is not None:
        # Test with example headlines
        test = [
            'My biggest laugh reveal ever!',
            'Learning game development with Unity',
            'A tour of Japan\'s Kansai region',
            '12 things NOT to do in Europe'
        ]

        token_text = pad_sequences(tokenizer.texts_to_sequences(test), maxlen=500)
        preds = [round(i[0]) for i in model.predict(token_text)]

        for (headline, pred) in zip(test, preds):
            label = 'Clickbait' if pred == 1.0 else 'Not Clickbait'
            print("{} - {}".format(headline, label))

            # Get detailed prediction with clickbait words
            result = predict_clickbait(model, tokenizer, headline)
            print(f"  Probability: {result['probability']:.2f}")
            print(f"  Clickbait words: {result['clickbait_words']}")
            print()