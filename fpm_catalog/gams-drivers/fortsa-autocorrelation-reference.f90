! Original L10a2a API driver. MIT: licenses/applied-methods-drivers-MIT.txt.
program main
   use iso_c_binding, only: c_double,c_int
   use fortsa_stats_m, only: acvf,acvf_opt,acvf2acf
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer(c_int),parameter :: n=8,m=8
   real(c_double),parameter :: base(n)=[1._c_double,-1._c_double,2._c_double,-2._c_double, &
      3._c_double,-3._c_double,4._c_double,-4._c_double]
   real(c_double) :: series(n),centered(n),reference(m),actual(m,3),average,error,maximum_error
   integer :: c,i,lag,method,covariance_calls,correlation_calls
   covariance_calls=0; correlation_calls=0; maximum_error=0
   do c=1,4
      select case(c)
      case(1)
         series=base
      case(2)
         series=base+10
      case(3)
         series=-2*base+3
      case(4)
         series=7
      end select
      average=0
      do i=1,n
         average=average+series(i)/n
      end do
      centered=series-average
      do lag=0,m-1
         reference(lag+1)=0
         do i=1,n-lag
            reference(lag+1)=reference(lag+1)+centered(i)*centered(i+lag)/n
         end do
      end do
      if(c==1) then
         if(any(abs(reference([1,2,8])-[7.5_c_double,-6.25_c_double,-.5_c_double])>1.e-12_c_double)) &
            error stop 'known covariance anchors'
      end if
      call acvf(series,n,actual(:,1),m)
      call acvf_opt(series,n,0_c_int,actual(:,2),m)
      call acvf_opt(series,n,1_c_int,actual(:,3),m)
      do method=1,3
         if(.not.all(ieee_is_finite(actual(:,method)))) error stop 'nonfinite autocovariance'
         error=maxval(abs(actual(:,method)-reference))
         maximum_error=max(maximum_error,error)
         if(error>1.e-10_c_double) error stop 'independent lag sums'
         covariance_calls=covariance_calls+1
         if(reference(1)>0) then
            call acvf2acf(actual(:,method),m)
            if(.not.all(ieee_is_finite(actual(:,method)))) error stop 'nonfinite autocorrelation'
            error=maxval(abs(actual(:,method)-reference/reference(1)))
            maximum_error=max(maximum_error,error)
            if(error>1.e-10_c_double) error stop 'normalized autocovariance'
            correlation_calls=correlation_calls+1
         end if
      end do
      if(c==1) then
         print '(a)', 'Lag       Direct autocorrelation'
         do lag=0,m-1
            print '(i3,f24.14)',lag,actual(lag+1,1)
         end do
      end if
   end do
   if(covariance_calls/=12 .or. correlation_calls/=9) error stop 'case count'
   print '(a,2i5)', 'Covariance/correlation calls checked: ',covariance_calls,correlation_calls
   print '(a,es14.5)', 'Maximum absolute error: ',maximum_error
   print '(a)', 'Constant-series covariance checked; zero-variance correlation is undefined and is not requested.'
   print '(a)', 'PASS fortsa-autocorrelation-reference'
end program
