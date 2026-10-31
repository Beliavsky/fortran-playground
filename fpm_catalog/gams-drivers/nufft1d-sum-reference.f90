! Independent API consumer; MIT: licenses/spatial-nufft-drivers-MIT.txt.
program nonuniform_reference
   use, intrinsic :: iso_fortran_env, only: real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: dp = real64, n = 80, mode_counts(*) = [15,16,31,32]
   real(dp), parameter :: pi = acos(-1._dp), requested = 1.e-10_dp
   real(dp) :: nodes(n),angle,re,im,scale,error
   complex(dp) :: strengths(n),reference
   complex(dp), allocatable :: transform(:)
   integer :: i,j,k,sign,m,case_number,pattern,calls
   interface
      subroutine nufft1d1f90(nj,xj,cj,iflag,eps,ms,fk,ier)
         import dp
         integer :: nj,iflag,ms,ier
         real(dp) :: xj(nj),eps
         complex(dp) :: cj(nj),fk(-ms/2:(ms-1)/2)
      end subroutine nufft1d1f90
   end interface
   block
      integer :: status
      do i = 1,n
         nodes(i) = pi*sin(.37_dp*i)+.01_dp*cos(.11_dp*i)
      end do
      ! Keep every source strictly inside the documented interval [-pi,pi].
      nodes = .95_dp*nodes
      calls = 0
      do case_number = 1,size(mode_counts)
         m = mode_counts(case_number)
         allocate(transform(-m/2:(m-1)/2))
         do pattern = 1,3
            strengths = cmplx(0._dp,0._dp,dp)
            select case(pattern)
            case(1)
               strengths(7) = cmplx(2._dp,-.5_dp,dp)
            case(2)
               strengths = cmplx(1._dp,0._dp,dp)
            case(3)
               do i = 1,n
                  strengths(i) = cmplx(real(mod(7*i,19)-9,dp)/8,real(mod(11*i,23)-11,dp)/8,dp)
               end do
            end select
            scale = max(1._dp,sum(abs(strengths))/n)
            do sign = -1,1,2
               call nufft1d1f90(n,nodes,strengths,sign,requested,m,transform,status)
               if (status /= 0) error stop 'NUFFT status'
               if (.not. all(ieee_is_finite(real(transform,dp)))) error stop 'nonfinite NUFFT real output'
               if (.not. all(ieee_is_finite(aimag(transform)))) error stop 'nonfinite NUFFT imaginary output'
               error = 0._dp
               do k = -m/2,(m-1)/2
                  re = 0._dp
                  im = 0._dp
                  do j = 1,n
                     angle = real(sign*k,dp)*nodes(j)
                     re = re+real(strengths(j),dp)*cos(angle)-aimag(strengths(j))*sin(angle)
                     im = im+real(strengths(j),dp)*sin(angle)+aimag(strengths(j))*cos(angle)
                  end do
                  reference = cmplx(re/n,im/n,dp)
                  error = max(error,abs(transform(k)-reference)/scale)
               end do
               if (error > 1.e-8_dp) error stop 'direct nonuniform Fourier sum'
               if (abs(transform(0)-sum(strengths)/n)/scale > 1.e-8_dp) error stop 'zero mode normalization'
               calls = calls+1
               print '(a,i0,a,i0,a,i2,a,es10.2)', 'Modes=',m,' signal=',pattern,' sign=',sign,' scaled error=',error
            end do
         end do
         deallocate(transform)
      end do
      if (calls /= 24) error stop 'NUFFT case count'
   end block
   print '(a)', '24 type-1 transforms checked against scalar Fourier sums, including odd/even mode counts and both signs.'
   print '(a)', 'PASS nufft1d-sum-reference'
end program nonuniform_reference
