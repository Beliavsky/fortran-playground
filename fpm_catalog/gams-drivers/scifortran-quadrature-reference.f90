! Independent API consumer; MIT: licenses/roots-splines-quadrature-drivers-MIT.txt.
module quadrature_reference_functions
   implicit none
   integer :: degree
   real(8) :: rate
contains
   real(8) function polynomial(t)
      real(8) :: t
      polynomial = t**degree
   end function polynomial
   real(8) function decay(t)
      real(8) :: t
      decay = exp(-rate*t)
   end function decay
   real(8) function gaussian(t)
      real(8) :: t
      gaussian = exp(-t*t)
   end function gaussian
   real(8) function cauchy(t)
      real(8) :: t
      cauchy = 1/(1+t*t)
   end function cauchy
   real(8) function root(t)
      real(8) :: t
      root = sqrt(t)
   end function root
   real(8) function inverse_root(t)
      real(8) :: t
      inverse_root = 1/sqrt(t)
   end function inverse_root
end module quadrature_reference_functions

program quadrature_reference
   use quadrature_reference_functions
   use SF_INTEGRATE, only: simps,trapz,quad
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: counts(*) = [5,8,9,16,17]
   real(8), parameter :: starts(*) = [-1.d0,0.d0,-.5d0],ends(*) = [1.d0,1.d0,1.5d0]
   real(8), parameter :: rates(*) = [.5d0,1.d0,2.d0]
   real(8), allocatable :: x(:),y(:)
   real(8) :: a,b,h,exact,trapezoid_exact,value,max_sample_error,max_quad_error
   integer :: interval,grid,n,i,key,j,sample_cases,quad_calls
   sample_cases = 0
   quad_calls = 0
   max_sample_error = 0.d0
   max_quad_error = 0.d0
   do interval = 1,3
      a = starts(interval)
      b = ends(interval)
      do grid = 1,size(counts)
         n = counts(grid)
         h = (b-a)/(n-1)
         allocate(x(n),y(n))
         x = [(a+real(i,8)*h,i=0,n-1)]
         do degree = 0,3
            y = x**degree
            exact = (b**(degree+1)-a**(degree+1))/(degree+1)
            trapezoid_exact = exact
            if (degree == 2) trapezoid_exact = exact+(b-a)*h*h/6
            if (degree == 3) trapezoid_exact = exact+(b*b-a*a)*h*h/4
            call check(simps(y,a,b),exact,2.d-12,max_sample_error)
            call check(simps(y,h),exact,2.d-12,max_sample_error)
            call check(trapz(y,a,b),trapezoid_exact,2.d-12,max_sample_error)
            call check(trapz(y,h),trapezoid_exact,2.d-12,max_sample_error)
            sample_cases = sample_cases+1
         end do
         deallocate(x,y)
      end do
      do degree = 0,7
         exact = (b**(degree+1)-a**(degree+1))/(degree+1)
         do key = 0,6
            if (key == 0) then
               call quad(polynomial,a,b,epsabs=1.d-11,epsrel=1.d-11,result=value)
            else
               call quad(polynomial,a,b,key=key,epsabs=1.d-11,epsrel=1.d-11,result=value)
            end if
            call checked_quad(exact)
         end do
      end do
   end do
   do i = 1,size(rates)
      rate = rates(i)
      do j = 0,1
         a = real(j,8)
         call quad(decay,a,inf=1,epsabs=1.d-11,epsrel=1.d-11,result=value)
         call checked_quad(exp(-rate*a)/rate)
      end do
   end do
   call quad(gaussian,0.d0,inf=2,epsabs=1.d-11,epsrel=1.d-11,result=value)
   call checked_quad(sqrt(acos(-1.d0)))
   call quad(cauchy,0.d0,inf=2,epsabs=1.d-11,epsrel=1.d-11,result=value)
   call checked_quad(acos(-1.d0))
   call quad(root,0.d0,1.d0,singular_endpoint=.true.,epsabs=1.d-11,epsrel=1.d-11,result=value)
   call checked_quad(2.d0/3)
   call quad(inverse_root,0.d0,1.d0,singular_endpoint=.true.,epsabs=1.d-11,epsrel=1.d-11,result=value)
   call checked_quad(2.d0)
   if (sample_cases /= 60 .or. quad_calls /= 178) error stop 'quadrature fixture count'
   print '(a)', '60 sampled-polynomial cases, 240 Simpson/trapezoid calls, even/odd panel counts.'
   print '(a)', '178 adaptive calls: polynomial rules, exponential tails, whole-line and endpoint-singular integrals.'
   print '(a,es12.4)', 'Maximum normalized sampled-rule reference error: ',max_sample_error
   print '(a,es12.4)', 'Maximum normalized adaptive closed-form error: ',max_quad_error
   print '(a)', 'PASS scifortran-quadrature-reference'
contains
   subroutine check(actual,reference,tolerance,maximum)
      real(8), intent(in) :: actual,reference,tolerance
      real(8), intent(inout) :: maximum
      real(8) :: error
      if (.not. ieee_is_finite(actual)) error stop 'nonfinite integral'
      error = abs(actual-reference)/max(1.d0,abs(reference))
      maximum = max(maximum,error)
      if (error > tolerance) error stop 'independent quadrature reference'
   end subroutine check
   subroutine checked_quad(reference)
      real(8), intent(in) :: reference
      call check(value,reference,5.d-11,max_quad_error)
      quad_calls = quad_calls+1
   end subroutine checked_quad
end program quadrature_reference
