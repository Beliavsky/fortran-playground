! Independently written grouped-binomial regression driver using the public API.
! No upstream test program or implementation is copied.
program checked_logistic_regression
   use Logistic_Regression, only: logistic,dp
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: groups=6
   integer :: trials(groups),successes(groups),ndf,status,problem,i
   real(dp) :: x(groups,1),beta(0:1),se(0:1),fit(groups),covariance(0:1,0:1),chisq,deviance
   real(dp) :: expected(groups),reference(0:1),low,high,logit_low,logit_high,levels(2)
   real(dp) :: fisher(0:1,0:1),exact_covariance(0:1,0:1),weight,determinant,dispersion
   real(dp) :: exact_chisq,exact_deviance,coefficient_error,covariance_error
   do problem=1,3
      trials=20
      if (problem<3) then
         successes=[3,5,7,13,15,17];low=0.25_dp;high=0.75_dp
      else
         successes=[2,4,6,10,12,14];low=0.2_dp;high=0.6_dp
      end if
      if (problem==2) then
         levels=[0._dp,2._dp]
      else
         levels=[-1._dp,1._dp]
      end if
      x(1:3,1)=levels(1);x(4:6,1)=levels(2)
      expected(1:3)=low;expected(4:6)=high
      ! At two predictor levels, the MLE fits each aggregated success proportion exactly.
      logit_low=log(low/(1._dp-low));logit_high=log(high/(1._dp-high))
      reference(1)=(logit_high-logit_low)/(levels(2)-levels(1))
      reference(0)=logit_low-reference(1)*levels(1)
      exact_chisq=0._dp;exact_deviance=0._dp;fisher=0._dp
      do i=1,groups
         weight=trials(i)*expected(i)*(1._dp-expected(i))
         exact_chisq=exact_chisq+(successes(i)-trials(i)*expected(i))**2/weight
         exact_deviance=exact_deviance+2._dp*(successes(i)*log(real(successes(i),dp)/(trials(i)*expected(i))) &
            +(trials(i)-successes(i))*log(real(trials(i)-successes(i),dp)/(trials(i)*(1._dp-expected(i)))))
         fisher(0,0)=fisher(0,0)+weight
         fisher(0,1)=fisher(0,1)+weight*x(i,1)
         fisher(1,1)=fisher(1,1)+weight*x(i,1)**2
      end do
      fisher(1,0)=fisher(0,1)
      determinant=fisher(0,0)*fisher(1,1)-fisher(0,1)**2
      exact_covariance(0,:)=[fisher(1,1),-fisher(0,1)]/determinant
      exact_covariance(1,:)=[-fisher(0,1),fisher(0,0)]/determinant
      ! This API inflates covariance by max(1,Pearson chi-square / residual degrees of freedom).
      dispersion=max(1._dp,exact_chisq/real(groups-2,dp))
      exact_covariance=dispersion*exact_covariance
      call logistic(groups,x,1,successes,trials,chisq,deviance,ndf,beta,se,status,cov_beta=covariance,fit=fit)
      if (status/=0.or.ndf/=groups-2) error stop 'logistic regression status or degrees of freedom'
      if (.not.all(ieee_is_finite(beta)).or..not.all(ieee_is_finite(fit)).or..not.all(ieee_is_finite(se))) &
         error stop 'nonfinite logistic result'
      if (.not.all(ieee_is_finite(covariance)).or..not.ieee_is_finite(chisq).or..not.ieee_is_finite(deviance)) &
         error stop 'nonfinite logistic statistics'
      if (any(fit<=0._dp).or.any(fit>=1._dp).or.any(se<=0._dp)) error stop 'invalid probabilities or standard errors'
      coefficient_error=maxval(abs(beta-reference))
      covariance_error=maxval(abs(covariance-exact_covariance))
      if (coefficient_error>1.e-6_dp.or.maxval(abs(fit-expected))>1.e-6_dp) error stop 'closed-form logistic fit mismatch'
      if (abs(chisq-exact_chisq)>1.e-6_dp.or.abs(deviance-exact_deviance)>1.e-6_dp) &
         error stop 'independent binomial statistic mismatch'
      if (covariance_error>1.e-5_dp) error stop 'Fisher covariance mismatch'
      if (maxval(abs(se-sqrt([exact_covariance(0,0),exact_covariance(1,1)])))>1.e-5_dp) &
         error stop 'standard error mismatch'
      print '(a,i0,a,i0)', 'Binomial case ',problem,' residual degrees of freedom=',ndf
      print '(a,2f16.10)', 'Fitted intercept/slope:',beta
      print '(a,2f16.10)', 'Exact intercept/slope: ',reference
      print '(a,2f16.10)', 'Pearson chi-square / deviance:',chisq,deviance
      print '(a,2f16.10)', 'Standard errors:',se
      print '(a,2es13.4)', 'Coefficient / covariance maximum errors:',coefficient_error,covariance_error
   end do
   print '(a)', 'PASS logistic-grouped-binomial-reference'
end program
