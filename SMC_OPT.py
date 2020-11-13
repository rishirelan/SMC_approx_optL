import numpy as np
from SMC_BASE import *
from scipy.stats import multivariate_normal as Normal_PDF

"""
A class of SMC sampler that builds on the SMC base class by allowing a
Gaussian approximation of the optimum L-kernel.

P.L.Green
"""


class SMC_OPT(SMC_BASE):

    def __init__(self, N, D, p, q0, K, q):
        """ Initialiser class method

        """

        # Initiate standard SMC sampler but with no L-kernel defined
        super().__init__(N, D, p, q0, K, q, L=None)

    def find_optL(self, x, x_new):
        """ Generate a Gaussian approximation of the optimum L-kernel.

        """

        # Collect x and x_new together into X
        X = np.hstack([x, x_new])

        # Directly estimate the mean and
        # covariance matrix of X
        mu_X = np.mean(X, axis=0)
        Sigma_X = np.cov(np.transpose(X))

        # Find mean of joint distribution (p(x, x_new))
        mu_x, mu_xnew = mu_X[0:self.D], mu_X[self.D:2 * self.D]

        # Find covariance matrix of joint distribution (p(x, x_new))
        (Sigma_x_x,
         Sigma_x_xnew,
         Sigma_xnew_x,
         Sigma_xnew_xnew) = (Sigma_X[0:self.D, 0:self.D],
                             Sigma_X[0:self.D, self.D:2 * self.D],
                             Sigma_X[self.D:2 * self.D, 0:self.D],
                             Sigma_X[self.D:2 * self.D, self.D:2 * self.D])

        def L_logpdf(x, x_cond):

            # Mean of approximately optimal L-kernel
            mu = (mu_x + Sigma_x_xnew @ np.linalg.inv(Sigma_xnew_xnew) @
                  (x_cond - mu_xnew))

            # Variance of approximately optimal L-kernel
            Sigma = (Sigma_x_x - Sigma_x_xnew @
                     np.linalg.inv(Sigma_xnew_xnew) @ Sigma_xnew_x)

            p = Normal_PDF(mean=mu, cov=Sigma)
            return p.logpdf(x)
        self.L = L_Kernel()
        self.L.logpdf = L_logpdf

    def update_weights(self, x, x_new, logw, p_log_pdf_x, p_log_pdf_x_new):
        """ Overwrites the method in the base-class

        """

        # Initialise arrays
        logw_new = np.vstack(np.zeros(self.N))

        # Find approximation of the optimum L-kernel
        self.find_optL(x, x_new)

        # Find new weights
        for i in range(self.N):

            logw_new[i] = (logw[i] +
                           p_log_pdf_x_new[i] -
                           p_log_pdf_x[i] +
                           self.L.logpdf(x=x[i], x_cond=x_new[i]) -
                           self.q.logpdf(x=x_new[i], x_cond=x[i]))

        return logw_new
