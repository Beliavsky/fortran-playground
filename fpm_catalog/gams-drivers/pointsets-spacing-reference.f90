! Independent API consumer; MIT: licenses/optimization-spacing-drivers-MIT.txt.
program spacing_reference
   use select_precision, only: wp
   use pointsets, only: arithmetic_spacing,geometric_spacing
   use, intrinsic :: iso_fortran_env, only: dp => real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: counts(*) = [2,3,5,9,17]
   real(wp), parameter :: starts(*) = [0._wp,-2._wp,3._wp,1._wp],ends(*) = [1._wp,3._wp,-2._wp,1._wp]
   real(wp), parameter :: ratios(*) = [.5_wp,.75_wp,1.25_wp,2._wp]
   real(wp) :: singleton(1),empty(0),guard(5),before(5)
   real(wp), allocatable :: x(:)
   real(dp), allocatable :: expected(:)
   real(dp) :: a,b,q,error,max_error,tolerance
   integer :: grid,interval,ratio,n,i,arithmetic_calls,geometric_calls,guards
   arithmetic_calls = 0
   geometric_calls = 0
   guards = 0
   max_error = 0._dp
   tolerance = 32*real(epsilon(1._wp),dp)
   do grid = 1,size(counts)
      n = counts(grid)
      allocate(x(n),expected(n))
      do interval = 1,4
         a = real(starts(interval),dp)
         b = real(ends(interval),dp)
         expected = [(a+(b-a)*real(i,dp)/(n-1),i=0,n-1)]
         call arithmetic_spacing(x,starts(interval),ends(interval))
         call check
         arithmetic_calls = arithmetic_calls+1
         do ratio = 1,4
            q = real(ratios(ratio),dp)
            expected = [(a+(b-a)*(q**i-1)/(q**(n-1)-1),i=0,n-1)]
            call geometric_spacing(x,starts(interval),ends(interval),ratios(ratio))
            call check
            geometric_calls = geometric_calls+1
         end do
      end do
      deallocate(x,expected)
   end do
   ! Guarded inputs are no-ops at this pin, rather than requests for a filled grid.
   singleton = 7._wp
   call arithmetic_spacing(singleton,0._wp,1._wp)
   if (singleton(1) /= 7) error stop 'arithmetic singleton guard'
   call geometric_spacing(singleton,0._wp,1._wp,2._wp)
   if (singleton(1) /= 7) error stop 'geometric singleton guard'
   call arithmetic_spacing(empty,0._wp,1._wp)
   call geometric_spacing(empty,0._wp,1._wp,2._wp)
   guards = 4
   before = [(real(i,wp),i=1,5)]
   do i = -1,1
      guard = before
      call geometric_spacing(guard,0._wp,1._wp,real(i,wp))
      if (any(guard /= before)) error stop 'geometric guarded ratio no-op'
      guards = guards+1
   end do
   if (arithmetic_calls /= 20 .or. geometric_calls /= 80 .or. guards /= 7) error stop 'spacing case count'
   print '(a,i0)', 'Working precision decimal digits: ',precision(1._wp)
   print '(a)', '20 arithmetic and 80 geometric grids; increasing, decreasing and equal endpoints.'
   print '(a,es12.4)', 'Maximum normalized error versus real64 formulas: ',max_error
   print '(a,es12.4)', 'Acceptance tolerance, 32 working-kind epsilons: ',tolerance
   print '(a)', 'Seven empty/singleton/ratio guards checked as unchanged-array behavior.'
   print '(a)', 'PASS pointsets-spacing-reference'
contains
   subroutine check
      if (.not. all(ieee_is_finite(x))) error stop 'nonfinite grid'
      error = maxval(abs(real(x,dp)-expected))/max(1._dp,abs(a),abs(b))
      max_error = max(max_error,error)
      if (error > tolerance) error stop 'independent spacing formula'
      if (abs(real(x(1),dp)-a) > tolerance*max(1._dp,abs(a))) error stop 'first endpoint'
      if (abs(real(x(n),dp)-b) > tolerance*max(1._dp,abs(b))) error stop 'last endpoint'
      if (b > a) then
         if (any(x(2:) <= x(:n-1))) error stop 'increasing grid'
      else if (b < a) then
         if (any(x(2:) >= x(:n-1))) error stop 'decreasing grid'
      else
         if (any(x /= starts(interval))) error stop 'constant grid'
      end if
   end subroutine check
end program spacing_reference
