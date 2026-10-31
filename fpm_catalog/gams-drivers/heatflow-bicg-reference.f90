! Independent API consumer; see licenses/sparse-advection-drivers-MIT.txt.
program checked_sparse_systems
   use constants, only: real12,int12
   use globe_data, only: ra
   use solver, only: SRSin,linbcg
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: sizes(4)=[5,9,17,33]
   real(real12), parameter :: scales(3)=[0.125_real12,1.0_real12,8.0_real12]
   real(real12), allocatable :: a(:,:),b(:),saved(:),x(:),exact(:),residual(:)
   real(real12) :: scale,error,solution_error,residual_error,worst_solution=0,worst_residual=0
   integer(int12) :: iterations
   integer :: s,n,family,q,shape,guess,i,j,solves=0,entries=0,matrices=0
   do s=1,size(sizes)
      n=sizes(s)
      allocate(a(n,n),b(n),saved(n),x(n),exact(n),residual(n))
      do family=1,3
         do q=1,3
            scale=scales(q); a=0
            do i=1,n
               a(i,i)=scale*(4+real(i,real12)/n)
               if (i>1) a(i,i-1)=-scale
               if (i<n) a(i,i+1)=-scale
               if (family>=2.and.i<n) a(i,i+1)=-0.5_real12*scale
               if (family==3.and.i>2) a(i,i-2)=0.25_real12*scale
               if (family==3.and.i<n-1) a(i,i+2)=-0.125_real12*scale
            end do
            call SRSin(a,0.0_real12,ra)
            if (ra%len/=count(a/=0)) error stop 'sparse storage count'
            matrices=matrices+1
            do shape=1,3
               do i=1,n
                  select case(shape)
                  case(1)
                     exact(i)=1
                  case(2)
                     exact(i)=(-1.0_real12)**i*(0.5_real12+real(i,real12)/n)
                  case(3)
                     exact(i)=0.25_real12+sin(real(3*i,real12)/n)
                  end select
               end do
               b=0
               do i=1,n
                  do j=1,n
                     b(i)=b(i)+a(i,j)*exact(j)
                  end do
               end do
               saved=b
               do guess=1,2
                  x=0
                  if (guess==2) x=[(0.1_real12*cos(real(i,real12)),i=1,n)]
                  iterations=0
                  call linbcg(b,x,1_int12,1e-11_real12,500_int12,iterations,error)
                  if (.not.all(ieee_is_finite(x)).or..not.ieee_is_finite(error)) error stop 'nonfinite solve'
                  if (iterations<1.or.iterations>500.or.error>1.01e-11_real12) error stop 'solver status'
                  residual=-b
                  do i=1,n
                     do j=1,n
                        residual(i)=residual(i)+a(i,j)*x(j)
                     end do
                  end do
                  solution_error=maxval(abs(x-exact))/(1+maxval(abs(exact)))
                  residual_error=maxval(abs(residual))/(1+maxval(abs(b)))
                  worst_solution=max(worst_solution,solution_error)
                  worst_residual=max(worst_residual,residual_error)
                  if (solution_error>2e-9_real12) error stop 'manufactured solution'
                  if (residual_error>2e-10_real12) error stop 'independent residual'
                  if (any(b/=saved)) error stop 'right hand side changed'
                  solves=solves+1; entries=entries+n
               end do
            end do
            deallocate(ra%val,ra%irow,ra%jcol)
         end do
      end do
      deallocate(a,b,saved,x,exact,residual)
   end do
   print '(a,i0)', 'Sparse matrices: ',matrices
   print '(a,i0)', 'BiCG solves: ',solves
   print '(a,i0)', 'Known solution entries: ',entries
   print '(a,es12.4)', 'Maximum normalized solution error: ',worst_solution
   print '(a,es12.4)', 'Maximum normalized true residual: ',worst_residual
   print '(a)', 'PASS heatflow-bicg-reference'
end program checked_sparse_systems
