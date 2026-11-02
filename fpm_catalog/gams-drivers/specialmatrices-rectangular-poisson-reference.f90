! Independent MIT consumer; see licenses/transforms-structures-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: wp=>real64
   use specialmatrices_poisson2D, only: Poisson2D,solve
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(Poisson2D) :: a
   real(wp),allocatable :: exact(:,:),rhs(:,:),b(:,:),saved(:,:),actual(:,:),vector(:),grid(:,:),residual(:,:)
   real(wp) :: lx,ly,hx,hy,x,y,pi,eigenvalue
   integer :: nx,ny,domain,problem,i,j,cases
   pi=acos(-1._wp); cases=0
   do nx=2,7
      do ny=2,7
         allocate(exact(nx,ny),rhs(nx,ny))
         do domain=1,2
            lx=real(domain,wp)/2; ly=real(domain+1,wp)/2
            hx=lx/real(nx+1,wp); hy=ly/real(ny+1,wp); a=Poisson2D(nx,ny,lx,ly)
            do problem=1,2
               eigenvalue=-4*sin(pi/(2*real(nx+1,wp)))**2/hx**2 &
                  -4*sin(pi/real(ny+1,wp))**2/hy**2
               do j=1,ny
                  y=hy*j
                  do i=1,nx
                     x=hx*i
                     if(problem==1) then
                        exact(i,j)=x*(lx-x)*y*(ly-y)
                        rhs(i,j)=-2*(x*(lx-x)+y*(ly-y))
                     else
                        exact(i,j)=sin(pi*real(i,wp)/real(nx+1,wp))*sin(2*pi*real(j,wp)/real(ny+1,wp))
                        rhs(i,j)=eigenvalue*exact(i,j)
                     end if
                  end do
               end do
               b=reshape([reshape(rhs,[nx*ny]),2*reshape(rhs,[nx*ny])],[nx*ny,2]); saved=b
               actual=solve(a,b); vector=solve(a,b(:,1)); grid=reshape(actual(:,1),[nx,ny])
               residual=-2*(1/hx**2+1/hy**2)*grid
               residual(2:nx,:)=residual(2:nx,:)+grid(:nx-1,:)/hx**2
               residual(:nx-1,:)=residual(:nx-1,:)+grid(2:nx,:)/hx**2
               residual(:,2:ny)=residual(:,2:ny)+grid(:,:ny-1)/hy**2
               residual(:,:ny-1)=residual(:,:ny-1)+grid(:,2:ny)/hy**2
               do j=1,ny
                  do i=1,nx
                     call check(grid(i,j),exact(i,j)); call check(residual(i,j),rhs(i,j))
                     call check(vector(i+(j-1)*nx),exact(i,j))
                     call check(actual(i+(j-1)*nx,2),2*exact(i,j))
                  end do
               end do
               if(any(b/=saved)) error stop 'Poisson RHS preservation'
               cases=cases+2
            end do
         end do
         deallocate(exact,rhs)
      end do
   end do
   print '(a,i0)', 'Rectangular homogeneous-Dirichlet Laplacian vector/multiple-RHS solves: ',cases
   print '(a)', 'PASS specialmatrices-rectangular-poisson-reference'
contains
   subroutine check(actual,expected)
      real(wp),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-9_wp*max(1._wp,abs(expected))) error stop 'Independent reference'
   end subroutine
end program
