import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

class QuinielaModel:

    def train(self, X_train, y_train):
        # Crear el clasificador RandomForest
        self.rf_classifier = RandomForestClassifier()

        # Definir los parámetros que deseas ajustar
        param_grid = {
            'n_estimators': [50, 100, 150],
            'max_depth': [None, 10],
            'min_samples_split': [2, 5],
            'min_samples_leaf': [1, 2]
        }

        # Configurar la búsqueda de cuadrícula
        grid_search = GridSearchCV(estimator=self.rf_classifier, param_grid=param_grid, cv=5, scoring='accuracy')

        # Realizar la búsqueda de cuadrícula en los datos de entrenamiento
        grid_search.fit(X_train, y_train)

        # Obtener el modelo con los mejores parámetros
        self.best_rf_model = grid_search.best_estimator_
        
        self.best_rf_model.fit(X_train, y_train)
        pass

    def predict(self, X_test):
        y_pred = self.best_rf_model.predict(X_test)
        return y_pred

    @classmethod
    def load(cls, filename):
        """ Load model from file """
        with open(filename, "rb") as f:
            model = pickle.load(f)
            assert type(model) == cls
        return model

    def save(self, filename):
        """ Save a model in a file """
        with open(filename, "wb") as f:
            pickle.dump(self, f)
