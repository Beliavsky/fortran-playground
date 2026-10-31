! Independent API consumer; see licenses/propack-fmm-drivers-MIT.txt.
program checked_fmm2d
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   interface
      subroutine rfmm2d_t_c_p(eps,ns,sources,charge,nt,targ,pottarg,ier)
         import real64
         integer :: ns,nt,ier
         real(real64) :: eps,sources(2,ns),charge(ns),targ(2,nt),pottarg(nt)
      end subroutine rfmm2d_t_c_p
   end interface
   integer, parameter :: counts(5)=[1,7,64,257,1024],nt=24
   integer :: s,geometry,pattern,accuracy,order,calls=0,references=0
   real(real64) :: worst(2)=0
   do s=1,5
      do geometry=1,2
         do pattern=1,3
            do accuracy=1,2
               do order=1,2
                  call fixture(counts(s),geometry,pattern,accuracy,order)
               end do
            end do
         end do
      end do
   end do
   print '(a,i0)', 'FMM potential calls: ',calls
   print '(a,i0)', 'Direct target references: ',references
   print '(a,es12.4)', 'Maximum cancellation-scaled error at eps=1e-6: ',worst(1)
   print '(a,es12.4)', 'Maximum cancellation-scaled error at eps=1e-10: ',worst(2)
   print '(a)', 'PASS fmm2d-laplace-reference'
contains
   subroutine fixture(ns,geometry,pattern,accuracy,order)
      integer, intent(in) :: ns,geometry,pattern,accuracy,order
      real(real64) :: sources(2,ns),charge(ns),targets(2,nt),potential(nt),direct(nt),magnitude(nt)
      real(real64) :: saved_sources(2,ns),saved_charge(ns),saved_targets(2,nt),eps,bound,x,y,term,error,radius
      integer :: i,j,source,status
      do i=1,ns
         source=i
         if (order==2) source=ns+1-i
         x=real(mod(37*source,2017),real64)/2017
         y=real(mod(113*source,2027),real64)/2027
         if (geometry==2) then
            x=0.01_real64*x+0.75_real64*mod(source,2)
            y=0.01_real64*y+0.75_real64*mod(source,2)
         end if
         sources(:,i)=[x,y]
         select case(pattern)
         case(1)
            charge(i)=1.0_real64/ns
         case(2)
            charge(i)=real((-1)**source,real64)*(1+real(mod(source,5),real64)/8)/ns
         case(3)
            charge(i)=(real(source,real64)-real(ns+1,real64)/2)/real(ns,real64)**2
         end select
      end do
      do i=1,nt
         if (i<=8) then
            targets(:,i)=[0.11_real64+0.07_real64*i,0.23_real64+0.031_real64*i]
         else if (i<=16) then
            targets(:,i)=[0.03_real64+0.001_real64*i,0.02_real64+0.002_real64*i]
         else
            targets(:,i)=[2.0_real64+0.1_real64*i,-1.0_real64+0.03_real64*i]
         end if
      end do
      saved_sources=sources; saved_charge=charge; saved_targets=targets
      eps=1e-6_real64; bound=2e-5_real64
      if (accuracy==2) then
         eps=1e-10_real64; bound=2e-8_real64
      end if
      call rfmm2d_t_c_p(eps,ns,sources,charge,nt,targets,potential,status)
      if (status/=0) error stop 'FMM status'
      if (.not.all(ieee_is_finite(potential))) error stop 'nonfinite potential'
      if (any(sources/=saved_sources).or.any(charge/=saved_charge).or.any(targets/=saved_targets)) &
         error stop 'FMM input changed'
      direct=0; magnitude=0
      do i=1,nt
         do j=1,ns
            radius=norm2(saved_targets(:,i)-saved_sources(:,j))
            if (radius<1e-12_real64) error stop 'coincident source/target fixture'
            term=saved_charge(j)*log(radius)
            direct(i)=direct(i)+term
            magnitude(i)=magnitude(i)+abs(term)
         end do
      end do
      ! Scale by unsigned contributions, so cancellation does not make the test ill-defined.
      error=maxval(abs(potential-direct)/max(1e-12_real64,magnitude))
      worst(accuracy)=max(worst(accuracy),error)
      if (error>bound) error stop 'direct Laplace sum mismatch'
      calls=calls+1; references=references+nt
   end subroutine fixture
end program checked_fmm2d
