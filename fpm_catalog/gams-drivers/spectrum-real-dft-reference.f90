! Independent API consumer; MIT: licenses/storage-fourier-geometry-drivers-MIT.txt.
program real_dft_reference
   use spectrum, only: rfft
   use, intrinsic :: iso_fortran_env, only: real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: dp = real64, lengths(*) = [3,4,5,6,7,8,11,12,15,16]
   real(dp), parameter :: pi = acos(-1._dp), tol = 1.e-11_dp
   real(dp), allocatable :: x(:), adjusted(:)
   complex(dp), allocatable :: actual(:)
   integer :: l, n, i, mode, calls
   calls = 0
   do l = 1, size(lengths)
      n = lengths(l)
      allocate(x(n))
      do mode = 1, 4
         do i = 1, n
            select case(mode)
            case(1)
               x(i) = 0._dp
               if (i == 2) x(i) = 1._dp
            case(2)
               x(i) = 2._dp
            case(3)
               x(i) = real(mod(7*i,11)-5,dp)/4
            case(4)
               x(i) = 1._dp + 2*cos(2*pi*(i-1)/n) - .5_dp*sin(2*pi*(i-1)/n)
            end select
         end do
         actual = rfft(x)
         call check(x,actual)
         calls = calls+1
      end do
      print '(a,i0,a)', 'Four signals checked at length ',n,' (direct DFT and Parseval)'
      deallocate(x)
   end do
   x = [1._dp,-2._dp,3._dp,.5_dp,4._dp]
   adjusted = [x,0._dp,0._dp,0._dp]
   actual = rfft(x,8)
   call check(adjusted,actual)
   actual = rfft(x,3)
   call check(x(:3),actual)
   calls = calls+2
   if (calls /= 42) error stop 'transform count'
   print '(a)', '42 forward real transforms checked, including explicit zero padding and truncation.'
   print '(a)', 'PASS spectrum-real-dft-reference'
contains
   subroutine check(signal,transform)
      real(dp), intent(in) :: signal(:)
      complex(dp), intent(in) :: transform(:)
      real(dp) :: re, im, angle, energy, reference_energy, scale
      integer :: n, k, j, weight
      n = size(signal)
      if (size(transform) /= n/2+1) error stop 'real half-spectrum length'
      if (.not. all(ieee_is_finite(real(transform,dp)))) error stop 'nonfinite DFT real part'
      if (.not. all(ieee_is_finite(aimag(transform)))) error stop 'nonfinite DFT imaginary part'
      scale = max(1._dp,sum(abs(signal)))
      energy = 0._dp
      do k = 0, n/2
         re = 0._dp
         im = 0._dp
         do j = 0, n-1
            angle = 2*pi*real(k*j,dp)/n
            re = re+signal(j+1)*cos(angle)
            im = im-signal(j+1)*sin(angle)
         end do
         if (abs(transform(k+1)-cmplx(re,im,dp))/scale > tol) error stop 'independent Fourier sum'
         weight = 2
         if (k == 0 .or. (mod(n,2) == 0 .and. k == n/2)) weight = 1
         energy = energy+weight*abs(transform(k+1))**2/n
      end do
      reference_energy = sum(signal**2)
      if (abs(energy-reference_energy)/max(1._dp,reference_energy) > tol) error stop 'Parseval energy'
      if (abs(aimag(transform(1))) > tol) error stop 'imaginary DC term'
      if (mod(n,2) == 0) then
         if (abs(aimag(transform(size(transform)))) > tol) error stop 'imaginary Nyquist term'
      end if
   end subroutine check
end program real_dft_reference
