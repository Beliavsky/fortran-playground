! Independent API consumer; MIT: licenses/rules-differences-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real32,real64
   use ieee_arithmetic, only: ieee_is_finite
   use mod_diff, only: diff_centered,diff_upwind
   implicit none
   integer,parameter::sizes(*)=[16,32,64,128,256]
   real(real64),parameter::phases(*)=[0.0_real64,0.37_real64,1.1_real64]
   real(real32),allocatable::f(:),dc(:),du(:)
   real(real64),allocatable::ec(:),eu(:),truth(:)
   real(real64)::pi,h,kh,theta,s,c,phase,tol,error,worst
   real(real64)::rc(5),ru(5),ratio_c,ratio_u,minimum_c,minimum_u
   integer::j,n,k,ip,kind,i,cases,fixtures,left,right
   pi=acos(-1.0_real64); worst=0; cases=0; fixtures=0
   minimum_c=huge(1.0_real64); minimum_u=minimum_c
   do j=1,size(sizes)
      n=sizes(j); h=2*pi/n
      allocate(f(n),ec(n),eu(n),truth(n))
      do k=1,3
         kh=k*h
         do ip=1,size(phases)
            phase=phases(ip)
            do kind=1,2
               do i=1,n
                  theta=k*(i-1)*h+phase; s=sin(theta); c=cos(theta)
                  if (kind==1) then
                     f(i)=real(s,real32)
                     ec(i)=sin(kh)*c/h
                     eu(i)=((1-cos(kh))*s+sin(kh)*c)/h
                     truth(i)=k*c
                  else
                     f(i)=real(c,real32)
                     ec(i)=-sin(kh)*s/h
                     eu(i)=((1-cos(kh))*c-sin(kh)*s)/h
                     truth(i)=-k*s
                  end if
               end do
               dc=diff_centered(f); du=diff_upwind(f)
               if (.not.all(ieee_is_finite(dc)).or..not.all(ieee_is_finite(du))) error stop 'nonfinite'
               error=max(maxval(abs(real(dc,real64)/h-ec)),maxval(abs(real(du,real64)/h-eu)))
               worst=max(worst,error)
               tol=8*epsilon(1.0_real32)/h
               if (error>tol) error stop 'Fourier discrete derivative'
               if (k==1.and.ip==1.and.kind==1) then
                  rc(j)=sqrt(sum((real(dc,real64)/h-truth)**2)/n)
                  ru(j)=sqrt(sum((real(du,real64)/h-truth)**2)/n)
               end if
               cases=cases+1
            end do
         end do
      end do
      ! Exactly representable nonsmooth data exercise both wraparound boundaries.
      do i=1,n
         f(i)=real(modulo(17*i+3,31)-15,real32)/8
      end do
      dc=diff_centered(f); du=diff_upwind(f)
      do i=1,n
         left=modulo(i-2,n)+1; right=modulo(i,n)+1
         if (dc(i)/=(f(right)-f(left))/2) error stop 'centered periodic indexing'
         if (du(i)/=f(i)-f(left)) error stop 'upwind periodic indexing'
      end do
      if (sum(real(dc,real64))/=0.or.sum(real(du,real64))/=0) error stop 'periodic telescoping'
      f=3.25_real32
      dc=diff_centered(f); du=diff_upwind(f)
      if (any(dc/=0).or.any(du/=0)) error stop 'constant derivative'
      fixtures=fixtures+2
      print '(a,i0,a,2es13.5)', 'N=',n,'; centered/upwind RMS errors: ',rc(j),ru(j)
      deallocate(f,ec,eu,truth,dc,du)
   end do
   do j=2,size(sizes)
      ratio_c=rc(j-1)/rc(j); ratio_u=ru(j-1)/ru(j)
      if (ratio_c<3.8_real64.or.ratio_c>4.2_real64) error stop 'second-order convergence'
      if (ratio_u<1.9_real64.or.ratio_u>2.1_real64) error stop 'first-order convergence'
      minimum_c=min(minimum_c,ratio_c); minimum_u=min(minimum_u,ratio_u)
   end do
   if (cases/=90.or.fixtures/=10) error stop 'fixture accounting'
   print '(a,i0,a,i0)', 'Fourier fixtures: ',cases,'; nonsmooth/constant fixtures: ',fixtures
   print '(a,es12.4)', 'Maximum exact-discrete derivative error: ',worst
   print '(a,2f10.5)', 'Minimum refinement ratios, centered/upwind: ',minimum_c,minimum_u
   print '(a)', 'PASS tsunami-differences-reference'
end program main
