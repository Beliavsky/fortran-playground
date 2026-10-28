program main
   use Logistic_Regression, only: logistic,dp
   implicit none
   integer, parameter :: groups=6
   integer :: trials(groups),successes(groups),ndf,ier,i
   real(dp) :: x(groups,1),beta(0:1),se(0:1),fit(groups),chisq,deviance,expected(groups)
   ! Two predictor levels, each repeated three times: the exact fitted
   ! probabilities are 1/4 and 3/4, so beta=(0,log(3)). No data download.
   x(:,1)=[-1._dp,-1._dp,-1._dp,1._dp,1._dp,1._dp]
   trials=20; successes=[5,5,5,15,15,15]
   expected=real(successes,dp)/real(trials,dp)
   call logistic(groups,x,1,successes,trials,chisq,deviance,ndf,beta,se,ier,fit=fit)
   if (ier/=0) error stop 'Logistic regression failed'
   if (maxval(abs(fit-expected))>1e-6_dp) error stop 'Incorrect fitted probabilities'
   if (abs(beta(0))>1e-6_dp.or.abs(beta(1)-log(3._dp))>1e-6_dp) error stop
   print '(a,2f14.8)', 'Intercept and slope:',beta
   do i=1,groups
      print '(a,f5.1,a,f10.6)', 'x=',x(i,1),'  fitted probability=',fit(i)
   end do
   print *, 'PASS lib_statistics'
end program main
