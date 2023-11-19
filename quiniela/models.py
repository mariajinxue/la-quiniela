import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

class QuinielaModel:

    def train(self, X_train, y_train, seasons):
        if seasons == "all":
            self.rf_model = RandomForestClassifier(max_depth=15, min_samples_leaf=2, min_samples_split=5, n_estimators=150)
            self.rf_model.fit(X_train, y_train)
        else:
            self.rf_classifier = RandomForestClassifier()
            
            param_grid = {
                'n_estimators': [50, 100, 150],
                'max_depth': [10, 15, 20],
                'min_samples_split': [2, 5],
                'min_samples_leaf': [1, 2]
            }

            grid_search = GridSearchCV(estimator=self.rf_classifier, param_grid=param_grid, cv=5, scoring='accuracy')
            grid_search.fit(X_train, y_train)

            self.rf_model = grid_search.best_estimator_
            
            self.rf_model.fit(X_train, y_train)
        pass

    def predict(self, X_test):
        y_pred = self.rf_model.predict(X_test)
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
