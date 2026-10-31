! Independent API consumer; MIT: licenses/pde-drivers-MIT.txt.
program periodic_reference
   use poisfft, only: drp, PoisFFT_Solver1D_DP, PoisFFT_Periodic, PoisFFT_Spectral, &
      PoisFFT_Estimate, Execute, Finalize
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(drp), parameter :: pi = acos(-1._drp), length = 2*pi
   integer, parameter :: grids(*) = [16,32,64], modes(*) = [PoisFFT_Spectral,2]
   real(drp) :: error,previous,ratio
   integer :: mode,g
   do mode = 1,size(modes)
      previous = 0._drp
      do g = 1,size(grids)
         call check(grids(g),modes(mode),error)
         if (mode == 2 .and. g > 1) then
            ratio = previous/error
            if (.not. ieee_is_finite(ratio)) error stop 'nonfinite periodic refinement ratio'
            if (ratio < 3.5_drp .or. ratio > 4.5_drp) error stop 'second-order periodic refinement'
         end if
         previous = error
      end do
   end do
   print '(a)', 'Spectral and second-order periodic Poisson solvers checked at three grids; plans reused for zero forcing.'
   print '(a)', 'PASS poisfft-periodic-reference'
contains
   subroutine check(n,approximation,continuous_error)
      integer, intent(in) :: n,approximation
      real(drp), intent(out) :: continuous_error
      type(PoisFFT_Solver1D_DP) :: solver
      real(drp) :: forcing(n), solution(n), continuous(n), discrete(n), h,x,mu1,mu3
      real(drp) :: solver_error,residual,term
      integer :: i,left,right
      h = length/n
      if (approximation == PoisFFT_Spectral) then
         mu1 = -1._drp
         mu3 = -9._drp
      else
         mu1 = -4*sin(pi/n)**2/h**2
         mu3 = -4*sin(3*pi/n)**2/h**2
      end if
      do i = 1,n
         x = (i-1)*h
         continuous(i) = sin(x)+.25_drp*cos(3*x)
         forcing(i) = -sin(x)-2.25_drp*cos(3*x)
         discrete(i) = -sin(x)/mu1-2.25_drp*cos(3*x)/mu3
      end do
      ! Periodic Poisson requires zero-mean forcing; remove only roundoff-level mean.
      forcing = forcing-sum(forcing)/n
      solver = PoisFFT_Solver1D_DP([n],[length],[PoisFFT_Periodic,PoisFFT_Periodic], &
         approximation=approximation,planning=PoisFFT_Estimate)
      call Execute(solver,solution,forcing)
      if (.not. all(ieee_is_finite(solution))) error stop 'nonfinite periodic solution'
      solver_error = maxval(abs(solution-discrete))
      if (solver_error > 1.e-11_drp) error stop 'exact periodic reference solution'
      if (abs(sum(solution)/n) > 1.e-11_drp) error stop 'zero-mean solution gauge'
      if (approximation == 2) then
         residual = 0._drp
         do i = 1,n
            left = modulo(i-2,n)+1
            right = modulo(i,n)+1
            term = (solution(left)-2*solution(i)+solution(right))/h**2-forcing(i)
            residual = max(residual,abs(term))
         end do
         if (residual/max(1._drp,maxval(abs(forcing))) > 1.e-11_drp) error stop 'periodic discrete residual'
      end if
      continuous_error = maxval(abs(solution-continuous))
      if (approximation == PoisFFT_Spectral .and. continuous_error > 1.e-11_drp) error stop 'spectral accuracy'
      print '(a,i0,a,i0,a,es10.2,a,es10.2)', 'Approximation=',approximation,' n=',n, &
         ' solver error=',solver_error,' continuous PDE error=',continuous_error
      forcing = 0._drp
      call Execute(solver,solution,forcing)
      if (.not. all(ieee_is_finite(solution))) error stop 'nonfinite zero-forcing solution'
      if (maxval(abs(solution)) > 1.e-11_drp) error stop 'reused plan zero forcing'
      call Finalize(solver)
   end subroutine check
end program periodic_reference
