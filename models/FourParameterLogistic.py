import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt


class FourParameterLogistic:
    '''
    Current problems: if a new y value is greater than 
    y_predicted, an error will be thrown. Numpy currently
    doesn't allow powers of negative numbers, even if it
    doesn't result in a complete number. We need to create 
    exception handling to catch this in the future. 
    '''
    def __init__(self, x, y):
        self.x = x
        self.y = y

        # Predicts likely initial parameters to optimize from.
        self.ip_min_y = min(y)
        self.ip_max_y = max(y)
        self.ip_ic50 = np.median(x)

        # Using the scipy minimize function to optimize from initial predicted parameters.
        initial_predictions = np.array([self.ip_min_y, self.ip_max_y, 1, self.ip_ic50])
        result = minimize(self.RSS, initial_predictions, method='Powell')
        self.fitted_params = result.x

    # Four-parameter function to calculate IC50 regression.
    def formula(self, X, min_y, max_y, hill_coeff, ic50):
        return max_y + ((min_y - max_y) / (1 + np.power((X / ic50), hill_coeff)))

    #Define prediction formula
    def predict_formula(self, Y, min_y, max_y, hill_coeff, ic50):
        '''
        Solve formula for X to allow unknown signal values (y)
        to return x values based on standard curve
        '''
        return ic50 * np.power((((min_y - max_y)/(Y - max_y)) - 1), (1/hill_coeff))

    # Returns the residual sum of squares between predicted and expected values.
    def RSS(self, init_params):
        predictions = self.formula(self.x, *init_params)
        return sum((self.y - predictions) ** 2)

    # Returns R-squared value of the determined regression.
    def r_2(self, verbose=True):
        model_predictions = self.formula(self.x, *self.fitted_params)
        abs_error = self.y - model_predictions
        r2 = 1.0 - (np.var(abs_error) / np.var(self.y))
        if verbose:
            return 'The R-squared value of the regression is ' + str(np.round(r2, 5)) + '.'
        else:
            return str(np.round(r2, 5))

    # Cleans up the parameters, labels them, and returns them.
    def parameters(self):
        minimum = self.fitted_params[0]
        maximum = self.fitted_params[1]
        hill_coeff = self.fitted_params[2]
        ic50 = self.fitted_params[3]
        params = [minimum, maximum, hill_coeff, ic50]
        params = [str(np.round(x, 2)) for x in params]
        labels = ['min: ', 'max: ', 'Hill coeff: ', 'IC50: ']
        params = [labels[i] + params[i] for i in range(len(params))]
        return params

    # Plots a comparison of the raw data with the calculated regression.
    def chart(self, x_labels=None, y_labels=None, plot_title=None):
        # Plotting the raw data.
        plt.scatter(self.x, self.y, c='b', s=30)

        # Plotting the regression.
        x_vals = np.arange(min(self.x), max(self.x), 0.1)
        y_preds = self.formula(x_vals, *self.fitted_params)
        plt.plot(x_vals, y_preds, c='b', label=f'R2: {self.r_2(verbose=False)}')
        if plot_title:
            plt.title(plot_title)
        if x_labels:
            plt.xlabel(x_labels)
        if y_labels:
            plt.ylabel(y_labels)
        plt.legend()
        return plt

    # Allows the user to enter a single value or a list to obtain predicted y value(s).
    def predict(self, user_input):
        prediction = self.predict_formula(user_input, *self.fitted_params)
        return prediction

    # Allows the user to add values of their own to the plotted regression.
    def chart_predictions(self, user_input, x_labels=None, y_labels=None, plot_title=None):
        predictions = self.predict(user_input)

        # Calls the plotted regression and adds the user input predictions.
        self.chart(x_labels, y_labels, plot_title)
        plt.scatter(predictions, user_input, c='r', s=30)
        plt.show()
        return self

#example data
def fourPL(x, ex_max, ex_min, ex_50, ex_hill):
    return ex_max + ((ex_min - ex_max) / (1 + np.power((x / ex_50), ex_hill)))

#create random data
rng = np.random.RandomState(12) #set for reproducibility

min_ = 1 + rng.rand(8)
max_ = 10 + rng.rand(8)
hill = 5.5 + rng.rand(8)
fixed_50 = 5

x = np.array([1, 1.5, 2, 3, 4, 6, 7, 8])

y = fourPL(x, max_, min_, fixed_50, hill)

plt.scatter(x, y)

#create new data to predict x values
rng2 = np.random.RandomState(1) #set for reproducibility
min_new = 1.2 + rng2.rand(16)
max_new = 9.8 + rng2.rand(16)
hill_new = 5.4 + rng2.rand(16)

x_new = np.linspace(1, 7, 16)
y_new = fourPL(x_new, max_new, min_new, fixed_50, hill_new)

#make class instance
model = FourParameterLogistic(x, y)
print(model.parameters())
model.chart_predictions(y_new, x_labels='Concentration', y_labels='MFI', plot_title='4PL fit')