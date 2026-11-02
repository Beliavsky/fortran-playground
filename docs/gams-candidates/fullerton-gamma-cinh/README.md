# Retained Fullerton gamma and Cinh probes

Each exact source has a normalized UTF-8/LF SHA256, package pin and complete hosted result. Neither upstream source nor numerical assertions were patched.

The original upper incomplete gamma probe built successfully but returned NaN on its first case a=1/2,x=0, where the integral equals sqrt(pi). Its diagnostic consumer is retained here. The initial consumer before diagnostic printing is also retained in ../fullerton-upper-gamma/. In fullerton_gamma.f90:307 the x<=0 rejection makes the following x==0 branch unreachable. The separate published positive-x consumer explicitly excludes this failed endpoint.

The Cinh (public inverse_chi) consumer built but failed at x=-3: actual 2.7167096138000488, reference 3.2845641411959674. Its full-domain record has no checked driver. The source series branch uses y=x*x/9-1 in fullerton_inv_ci.f90:85; whether this causes the mismatch requires further investigation. No positive/negative full-domain claim is made from other successful functions. A separate reciprocal-gamma pole-zero consumer replaces this candidate.
