! Independent MIT consumer; see licenses/roots-structured-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use SpecialMatrices,only:Poisson2D,eigh,eigvalsh
   implicit none
   real(wp),allocatable::w(:),v(:,:),z(:),a(:,:),ref(:)
   real(wp)::pi,hx,hy,t
   integer::nx,ny,n,i,j,k,p,q
   pi=acos(-1._wp)
   do nx=2,5
      do ny=2,4
         n=nx*ny;hx=2._wp/(nx+1);hy=3._wp/(ny+1)
         allocate(a(n,n),ref(n));a=0;k=0
         do j=1,ny
            do i=1,nx
               k=k+1;a(k,k)=-2/hx**2-2/hy**2
               if(i<nx) then
                  a(k,k+1)=1/hx**2;a(k+1,k)=1/hx**2
               end if
               if(j<ny) then
                  a(k,k+nx)=1/hy**2;a(k+nx,k)=1/hy**2
               end if
               ref(k)=-4*(sin(pi*i/(2*(nx+1)))/hx)**2-4*(sin(pi*j/(2*(ny+1)))/hy)**2
            end do
         end do
         do i=2,n
            t=ref(i);j=i-1
            do while(j>=1)
               if(ref(j)<=t) exit
               ref(j+1)=ref(j);j=j-1
            end do
            ref(j+1)=t
         end do
         call eigh(Poisson2D(nx,ny,2._wp,3._wp),w,v)
         z=eigvalsh(Poisson2D(nx,ny,2._wp,3._wp))
         do j=1,n
            call check(w(j),ref(j));call check(z(j),ref(j))
            do i=1,n
               call check(dot_product(a(i,:),v(:,j)),w(j)*v(i,j))
               call check(dot_product(v(:,i),v(:,j)),real(merge(1,0,i==j),wp))
            end do
         end do
         deallocate(a,ref,w,v,z)
      end do
   end do
   print '(a)', '12 rectangular Poisson spectra: stencil residuals and tensor-sine values checked.'
   print '(a)', 'PASS specialmatrices-poisson-eigenpairs-reference'
contains
   subroutine check(a,b)
      real(wp),intent(in)::a,b
      if(.not.ieee_is_finite(a)) error stop 'Nonfinite result'
      if(abs(a-b)>2.e-9_wp*max(1._wp,abs(b))) then
         print *, 'actual, reference:',a,b
         error stop 'Independent reference'
      end if
   end subroutine
end program
