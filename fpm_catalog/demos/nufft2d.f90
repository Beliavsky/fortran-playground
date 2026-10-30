program main
   use, intrinsic :: iso_fortran_env, only: real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: nj=96, ms=16, mt=18
   real(real64), parameter :: pi=acos(-1.0_real64), eps=1e-10_real64
   real(real64) :: x(nj), y(nj), error
   complex(real64) :: c(nj), fk(-ms/2:(ms-1)/2,-mt/2:(mt-1)/2)
   complex(real64) :: reference(-ms/2:(ms-1)/2,-mt/2:(mt-1)/2)
   integer :: j, k, l, sign, status
   interface
      subroutine nufft2d1f90(nj,xj,yj,cj,iflag,eps,ms,mt,fk,ier)
         import real64
         integer :: nj, iflag, ms, mt, ier
         real(real64) :: xj(nj), yj(nj), eps
         complex(real64) :: cj(nj), fk(-ms/2:(ms-1)/2,-mt/2:(mt-1)/2)
      end subroutine
   end interface
   do j=1, nj
      x(j) = pi*sin(0.71_real64*j)
      y(j) = pi*cos(0.43_real64*j)
      c(j) = cmplx(cos(0.13_real64*j), sin(0.17_real64*j), real64)
   end do
   do sign=-1, 1, 2
      call nufft2d1f90(nj, x, y, c, sign, eps, ms, mt, fk, status)
      if (status /= 0) error stop 'NUFFT returned an error'
      do l=-mt/2, (mt-1)/2
         do k=-ms/2, (ms-1)/2
            reference(k,l) = sum(c*exp(cmplx(0.0_real64, sign*(k*x+l*y), real64)))/nj
         end do
      end do
      if (.not. all(ieee_is_finite(real(fk))) .or. .not. all(ieee_is_finite(aimag(fk)))) &
         error stop 'nonfinite transform'
      error = maxval(abs(fk-reference))/max(1.0_real64,maxval(abs(reference)))
      print '(a,i2,a,es12.4)', 'Type 1, sign ', sign, ': scaled maximum error ', error
      if (error > 1e-8_real64) error stop 'transform differs from direct Fourier sum'
   end do
   print *, 'PASS nufft2d'
end program
