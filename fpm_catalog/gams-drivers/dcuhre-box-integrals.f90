! Adapted author API patterns; analytic integral and moment checks.
! ACM Software License Agreement
! ==============================
! 
! This software is based on Algorithm 698, DCUHRE, from the Collected
! Algorithms of the ACM (CALGO).
! 
! Original Work
! -------------
! Algorithm 698: DCUHRE: An Adaptive Multidimensional Integration Routine
! for a Vector of Integrals.
! 
! Authors:
!   Jarle Berntsen (University of Bergen, Norway)
!   Terje O. Espelid (University of Bergen, Norway)
!   Alan Genz (Washington State University, USA)
! 
! Published in:
!   ACM Transactions on Mathematical Software, Vol. 17, No. 4,
!   December 1991, pp. 452-456.
!   DOI: 10.1145/210232.210234
! 
! Copyright Notice
! ----------------
! Copyright (C) 1991 by ACM, Inc.
! 
! Use of ACM Algorithms is subject to the ACM Software Copyright and
! License Agreement: https://www.acm.org/publications/policies/software-copyright-notice
! 
! Permission to use, copy, modify, and redistribute this software and its
! documentation for any non-commercial purpose is hereby granted without
! fee, provided that the above copyright notice appear in all copies and
! that both that copyright notice and this permission notice appear in
! supporting documentation.
! 
! ACM makes no representations about the suitability of this software for
! any purpose. It is provided "as is" without express or implied warranty.
! 
! Derivative Work Notice
! ----------------------
! This modernised version is a derivative work prepared by Zane Hambly (2025).
! Modifications include conversion to modern Fortran standards while
! preserving the original algorithm and numerical accuracy.
! 
! The derivative work is distributed under the same ACM license terms as
! the original software.
module checked_integrands
   use iso_fortran_env, only: wp=>real64
   implicit none
contains
   subroutine integrand(ndim,x,nfun,f)
      integer, intent(in) :: ndim,nfun
      real(wp), intent(in) :: x(ndim)
      real(wp), intent(out) :: f(nfun)
      f(1)=sum(x*x)
      f(2)=exp(sum(x))
   end subroutine
end module
program checked_cubature
   use checked_integrands
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: nfun=2,nwork=10000,max_evaluations=20000
   real(wp), parameter :: epsabs=1.e-10_wp,epsrel=1.e-9_wp
   real(wp) :: result(nfun),estimate(nfun),exact(nfun),work(nwork),scaled_error
   real(wp), allocatable :: lower(:),upper(:),width(:)
   integer :: ndim,status,evaluations,j,k
   interface
      subroutine dcuhre(ndim,nfun,a,b,minpts,maxpts,fun,epsabs,epsrel,key,nw,restar, &
                        result,abserr,neval,ifail,work)
         import wp,integrand
         integer :: ndim,nfun,minpts,maxpts,key,nw,restar,neval,ifail
         real(wp) :: a(ndim),b(ndim),epsabs,epsrel,result(nfun),abserr(nfun),work(nw)
         procedure(integrand) :: fun
      end subroutine
   end interface
   do ndim=2,3
      allocate(lower(ndim),upper(ndim),width(ndim))
      if (ndim==2) then
         lower=0._wp;upper=1._wp
      else
         lower=[-1._wp,0._wp,1._wp];upper=[0._wp,2._wp,2._wp]
      end if
      width=upper-lower
      exact(1)=0._wp
      do j=1,ndim
         exact(1)=exact(1)+(upper(j)**3-lower(j)**3)/3._wp*product(width)/width(j)
      end do
      exact(2)=product(exp(upper)-exp(lower))
      call dcuhre(ndim,nfun,lower,upper,0,max_evaluations,integrand,epsabs,epsrel,0,nwork,0, &
         result,estimate,evaluations,status,work)
      if (status/=0) error stop 'adaptive cubature did not reach requested accuracy'
      if (evaluations<1.or.evaluations>max_evaluations) error stop 'evaluation budget mismatch'
      if (.not.all(ieee_is_finite(result)).or..not.all(ieee_is_finite(estimate))) error stop 'nonfinite integrals'
      if (any(estimate<0._wp).or.any(estimate>max(epsabs,epsrel*abs(result)))) error stop 'invalid error estimates'
      print '(a,i0,a,i0)', 'Dimensions=',ndim,' evaluations=',evaluations
      print '(a)', 'Integral / analytic value / estimated error / scaled analytic error'
      do k=1,nfun
         scaled_error=abs(result(k)-exact(k))/max(1._wp,abs(exact(k)))
         if (scaled_error>1.e-8_wp) error stop 'analytic integral mismatch'
         print '(4es19.10)',result(k),exact(k),estimate(k),scaled_error
      end do
      deallocate(lower,upper,width)
   end do
   print '(a)', 'PASS dcuhre-box-integrals'
end program
