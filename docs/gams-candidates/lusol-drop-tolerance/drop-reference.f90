! Independent API consumer; see licenses/sparse-spectra-drivers-MIT.txt.
program checked_sparse_updates
   use lusol, only: lu1fac,lu6sol,lu8rpc
   use lusol_precision, only: ip,wp=>rp
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer(ip), parameter :: sizes(4)=[2_ip,3_ip,5_ip,8_ip],capacity=10000_ip
   real(wp), parameter :: scales(2)=[0.25_wp,2.0_wp]
   integer(ip) :: indc(capacity),indr(capacity),luparm(30),status,n,i,j,k,column
   integer(ip), allocatable :: p(:),q(:),lenc(:),lenr(:),locc(:),locr(:),iploc(:),iqloc(:),ipinv(:),iqinv(:),rows(:)
   real(wp) :: a(capacity),parmlu(30),diag,vnorm,solution_error,residual_error
   real(wp) :: worst_solution=0,worst_residual=0
   real(wp), allocatable :: base(:,:),dense(:,:),work(:),v(:),x(:),exact(:),rhs(:),residual(:)
   integer :: s,family,scale_id,permutation,stage,pattern,direction,factors=0,updates=0,solves=0,entries=0
   do s=1,4
      n=sizes(s)
      allocate(p(n),q(n),lenc(n),lenr(n),locc(n),locr(n),iploc(n),iqloc(n),ipinv(n),iqinv(n),rows(n))
      allocate(base(n,n),dense(n,n),work(n),v(n),x(n),exact(n),rhs(n),residual(n))
      do family=1,2
         do scale_id=1,2
            do permutation=1,2
               base=0
               do i=1,n
                  base(i,i)=4+real(i,wp)/n
                  if (i>1) base(i,i-1)=-0.5_wp
                  if (i<n) base(i,i+1)=-1
                  if (family==2.and.i>2) base(i,i-2)=0.25_wp
                  if (family==2.and.i<n-1) base(i,i+2)=-0.125_wp
               end do
               rows=[(i,i=1,n)]
               if (permutation==2) then
                  rows(1)=n; rows(n)=1
               end if
               dense=scales(scale_id)*base(rows,:)
               a=0; indc=0; indr=0; k=0
               do j=1,n
                  do i=1,n
                     if (dense(i,j)==0) cycle
                     k=k+1; a(k)=dense(i,j); indc(k)=i; indr(k)=j
                  end do
               end do
               ! Public parameter defaults documented by the upstream EZ wrapper.
               luparm=0; luparm(1)=6; luparm(3)=5; luparm(8)=1
               parmlu=0
               parmlu(1:8)=[100.0_wp,10.0_wp,epsilon(1.0_wp)**0.8_wp,epsilon(1.0_wp)**0.67_wp, &
                  epsilon(1.0_wp)**0.67_wp,3.0_wp,0.3_wp,0.5_wp]
               call lu1fac(n,n,k,capacity,luparm,parmlu,a,indc,indr,p,q,lenc,lenr,locc,locr, &
                  iploc,iqloc,ipinv,iqinv,work,status)
               if (status/=0) error stop 'sparse LU factorization status'
               factors=factors+1
               do stage=0,2
                  if (stage>0) then
                     column=1
                     if (stage==2) column=n
                     do i=1,n
                        base(i,column)=0.125_wp*sin(real(i+2*stage,wp))
                     end do
                     base(column,column)=6+real(column,wp)/8
                     dense=scales(scale_id)*base(rows,:); v=dense(:,column)
                     call lu8rpc(1_ip,1_ip,n,n,column,v,work,capacity,luparm,parmlu,a,indc,indr,p,q, &
                        lenc,lenr,locc,locr,status,diag,vnorm)
                     if (status/=0) error stop 'column replacement status'
                     if (.not.all(ieee_is_finite([diag,vnorm]))) error stop 'nonfinite update diagnostics'
                     updates=updates+1
                  end if
                  do pattern=1,3
                     do i=1,n
                        select case(pattern)
                        case(1)
                           exact(i)=1
                        case(2)
                           exact(i)=(-1.0_wp)**i*(1+real(i,wp)/n)
                        case(3)
                           exact(i)=0.25_wp+sin(real(2*i,wp)/n)
                        end select
                     end do
                     do direction=1,2
                        rhs=0
                        do i=1,n
                           do j=1,n
                              if (direction==1) rhs(i)=rhs(i)+dense(i,j)*exact(j)
                              if (direction==2) rhs(i)=rhs(i)+dense(j,i)*exact(j)
                           end do
                        end do
                        if (direction==1) then
                           v=rhs; x=0
                           call lu6sol(5_ip,n,n,v,x,capacity,luparm,parmlu,a,indc,indr,p,q,lenc,lenr,locc,locr,status)
                        else
                           x=rhs; v=0
                           call lu6sol(6_ip,n,n,v,x,capacity,luparm,parmlu,a,indc,indr,p,q,lenc,lenr,locc,locr,status)
                           x=v
                        end if
                        if (status/=0.or..not.all(ieee_is_finite(x))) error stop 'sparse solve status'
                        residual=-rhs
                        do i=1,n
                           do j=1,n
                              if (direction==1) residual(i)=residual(i)+dense(i,j)*x(j)
                              if (direction==2) residual(i)=residual(i)+dense(j,i)*x(j)
                           end do
                        end do
                        solution_error=maxval(abs(x-exact))/(1+maxval(abs(exact)))
                        residual_error=maxval(abs(residual))/(1+maxval(abs(rhs)))
                        worst_solution=max(worst_solution,solution_error); worst_residual=max(worst_residual,residual_error)
                        if (solution_error>5e-12_wp.or.residual_error>5e-12_wp) then
                           print *, 'Solve fixture: ',n,family,scale_id,permutation,stage,pattern,direction
                           print *, 'Errors: ',solution_error,residual_error
                           print *, 'Actual: ',x
                           print *, 'Expected: ',exact
                           error stop 'known sparse solution'
                        end if
                        solves=solves+1; entries=entries+int(n)
                     end do
                  end do
               end do
            end do
         end do
      end do
      deallocate(p,q,lenc,lenr,locc,locr,iploc,iqloc,ipinv,iqinv,rows,base,dense,work,v,x,exact,rhs,residual)
   end do
   print '(a,i0)', 'Sparse LU factorizations: ',factors
   print '(a,i0)', 'Sequential column replacements: ',updates
   print '(a,i0)', 'Normal/transpose solves: ',solves
   print '(a,i0)', 'Known solution entries: ',entries
   print '(a,es12.4)', 'Maximum normalized solution error: ',worst_solution
   print '(a,es12.4)', 'Maximum normalized true residual: ',worst_residual
   print '(a)', 'PASS lusol-update-reference'
end program checked_sparse_updates
