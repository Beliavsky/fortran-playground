! Independent API consumer; MIT: licenses/pde-drivers-MIT.txt.
program helmholtz_reference
   use fishpack, only: wp, ip, hwscrt
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp), parameter :: shifts(*) = [0._wp,-.75_wp], pi = acos(-1._wp)
   real(wp) :: error, previous, ratio
   integer :: problem, refinement
   do problem = 1,size(shifts)
      previous = 0._wp
      do refinement = 0,2
         call check(16_ip*2**refinement,12_ip*2**refinement,shifts(problem),error)
         if (refinement > 0) then
            ratio = previous/error
            if (.not. ieee_is_finite(ratio)) error stop 'nonfinite refinement ratio'
            if (ratio < 3.8_wp .or. ratio > 4.2_wp) error stop 'second-order mesh refinement'
         end if
         previous = error
      end do
   end do
   print '(a)', 'Six nonzero-Dirichlet Poisson/Helmholtz solves checked against exact discrete solutions.'
   print '(a)', 'PASS fishpack-helmholtz-reference'
contains
   subroutine check(m,n,lambda,continuous_error)
      integer(ip), intent(in) :: m,n
      real(wp), intent(in) :: lambda
      real(wp), intent(out) :: continuous_error
      real(wp) :: solution(m+1,n+1), forcing(m+1,n+1), continuous(m+1,n+1), discrete(m+1,n+1)
      real(wp) :: dummy(1), perturbation, x,y,affine,wave,hx,hy,mu_continuous,mu_discrete,factor
      real(wp) :: solver_error,residual,term,boundary_error
      integer(ip) :: i,j,status
      hx = 2._wp/m
      hy = 2._wp/n
      mu_continuous = -(pi/2)**2-pi**2
      mu_discrete = -4*sin(pi/(2*m))**2/hx**2-4*sin(pi/n)**2/hy**2
      factor = (mu_continuous+lambda)/(mu_discrete+lambda)
      forcing = 0._wp
      do j = 1,n+1
         y = -1._wp+(j-1)*hy
         do i = 1,m+1
            x = (i-1)*hx
            affine = 1._wp+.5_wp*x-.25_wp*y
            wave = sin(pi*x/2)*sin(pi*(y+1._wp))
            continuous(i,j) = affine+wave
            discrete(i,j) = affine+factor*wave
            forcing(i,j) = lambda*affine+(mu_continuous+lambda)*wave
            if (i == 1 .or. i == m+1 .or. j == 1 .or. j == n+1) then
               solution(i,j) = affine
            else
               solution(i,j) = forcing(i,j)
            end if
         end do
      end do
      dummy = 0._wp
      call hwscrt(0._wp,2._wp,m,1_ip,dummy,dummy,-1._wp,1._wp,n,1_ip, &
         dummy,dummy,lambda,solution,m+1,perturbation,status)
      if (status /= 0) error stop 'Poisson/Helmholtz solver status'
      if (.not. all(ieee_is_finite(solution))) error stop 'nonfinite PDE solution'
      if (.not. ieee_is_finite(perturbation)) error stop 'nonfinite forcing perturbation'
      if (abs(perturbation) > 1.e-12_wp) error stop 'unexpected forcing perturbation'
      solver_error = maxval(abs(solution-discrete))
      if (solver_error > 1.e-11_wp) error stop 'exact discrete eigenmode solution'
      boundary_error = max(maxval(abs(solution(1,:)-continuous(1,:))), &
         maxval(abs(solution(m+1,:)-continuous(m+1,:))), &
         maxval(abs(solution(:,1)-continuous(:,1))),maxval(abs(solution(:,n+1)-continuous(:,n+1))))
      if (boundary_error > 1.e-12_wp) error stop 'nonzero boundary preservation'
      residual = 0._wp
      do j = 2,n
         do i = 2,m
            term = (solution(i-1,j)-2*solution(i,j)+solution(i+1,j))/hx**2 &
               +(solution(i,j-1)-2*solution(i,j)+solution(i,j+1))/hy**2 &
               +lambda*solution(i,j)-forcing(i,j)
            residual = max(residual,abs(term))
         end do
      end do
      residual = residual/max(1._wp,maxval(abs(forcing(2:m,2:n))))
      if (residual > 1.e-11_wp) error stop 'independent five-point residual'
      continuous_error = maxval(abs(solution-continuous))
      if (abs(continuous_error-abs(factor-1._wp)) > 1.e-11_wp) error stop 'predicted discretization error'
      print '(a,f6.2,a,i0,a,i0,a,es10.2,a,es10.2,a,es10.2)', 'lambda=',lambda,' grid=',m,'x',n, &
         ' solver error=',solver_error,' PDE error=',continuous_error,' residual=',residual
   end subroutine check
end program helmholtz_reference
