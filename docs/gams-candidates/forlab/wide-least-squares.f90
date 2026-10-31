! Independent API consumer; MIT: licenses/geodesy-forlab-drivers-MIT.txt.
program main
   use ieee_arithmetic,only:ieee_is_finite
   use forlab,only:solve,real64=>RPRE
   implicit none
   integer,parameter::shapes(2,5)=reshape([2,1,3,2,5,3,2,3,3,5],[2,5])
   real(real64),parameter::scales(*)=[-4.0_real64,0.5_real64,2.0_real64]
   real(real64),allocatable::a(:,:),saved_a(:,:),b(:,:),saved_b(:,:),left(:,:),right(:,:)
   real(real64),allocatable::expected(:,:),noise(:,:),x(:,:),v(:),r(:,:),d(:)
   real(real64)::value,z,rho,normalization,answer_error,residual_error,stationary,worst_x,worst_r,worst_s
   integer::shape_id,m,n,k,is,rotation,level,i,j,l,c,fixtures,calls,nonzero
   fixtures=0; calls=0; nonzero=0; worst_x=0; worst_r=0; worst_s=0
   do shape_id=1,size(shapes,2)
      m=shapes(1,shape_id); n=shapes(2,shape_id); k=min(m,n)
      allocate(a(m,n),saved_a(m,n),b(m,3),saved_b(m,3),left(m,m),right(n,n))
      allocate(expected(n,3),noise(m,3),r(m,3),d(k))
      do is=1,size(scales)
         d=[(real(i,real64)*scales(is),i=1,k)]
         do rotation=1,2
            call orthogonal_factor(left,rotation); call orthogonal_factor(right,rotation)
            a=0
            do j=1,n
               do i=1,m
                  do l=1,k
                     a(i,j)=a(i,j)+left(i,l)*d(l)*right(j,l)
                  end do
               end do
            end do
            do level=1,2
               rho=0
               if (level==2.and.m>n) rho=0.25_real64
               noise=0; expected=0
               do c=1,3
                  do j=1,n
                     do l=1,k
                        z=real(2*l-c,real64)/4
                        expected(j,c)=expected(j,c)+right(j,l)*z
                     end do
                  end do
                  if (m>n) noise(:,c)=rho*c*left(:,n+1)
               end do
               if (rho>0) nonzero=nonzero+1
               b=noise
               do c=1,3
                  do i=1,m
                     do j=1,n
                        b(i,c)=b(i,c)+a(i,j)*expected(j,c)
                     end do
                  end do
               end do
               saved_a=a; saved_b=b
               allocate(x(n,3))
               do c=1,3
                  v=solve(a,b(:,c))
                  if (size(v)/=n.or..not.all(ieee_is_finite(v))) then
                     print *, 'Failure m,n,scale,rotation,residual-level,RHS:',m,n,scales(is),rotation,level,c
                     print *, 'Matrix:',a
                     print *, 'RHS:',b(:,c)
                     error stop 'vector solution'
                  end if
                  x(:,c)=v
                  answer_error=maxval(abs(v-expected(:,c)))/max(1.0_real64,maxval(abs(expected(:,c))))
                  if (answer_error>3e-5_real64) error stop 'known minimum-norm solution'
                  worst_x=max(worst_x,answer_error)
                  calls=calls+1
               end do
               if (any(a/=saved_a).or.any(b/=saved_b)) error stop 'inputs changed'
               r=-b
               do c=1,3
                  do i=1,m
                     do j=1,n
                        r(i,c)=r(i,c)+a(i,j)*x(j,c)
                     end do
                  end do
               end do
               normalization=max(1.0_real64,maxval(abs(b)))
               residual_error=maxval(abs(r+noise))/normalization
               if (residual_error>5e-5_real64) error stop 'known residual'
               worst_r=max(worst_r,residual_error)
               stationary=0
               do c=1,3
                  do j=1,n
                     value=0
                     do i=1,m
                        value=value+a(i,j)*r(i,c)
                     end do
                     stationary=max(stationary,abs(value)/(normalization*max(1.0_real64,maxval(abs(a)))))
                  end do
                  value=abs(sum(r(:,c)**2)-(rho*c)**2)/max(1.0_real64,(rho*c)**2)
                  if (value>2e-4_real64) error stop 'known residual norm'
               end do
               if (stationary>1e-4_real64) error stop 'normal-equation residual'
               worst_s=max(worst_s,stationary)
               deallocate(x)
               fixtures=fixtures+1
            end do
         end do
      end do
      deallocate(a,saved_a,b,saved_b,left,right,expected,noise,r,d,v)
   end do
   if (fixtures/=60.or.calls/=180.or.nonzero/=18) error stop 'fixture accounting'
   print '(a,i0,a,i0)', 'Full-rank least-squares fixtures: ',fixtures,'; solver calls: ',calls
   print '(a,i0)', 'Overdetermined fixtures with prescribed nonzero residuals: ',nonzero
   print '(a)', 'Tall/wide; three vector RHS calls per fixture; catalog RPRE kind checked below.'
   print '(a,es12.4)', 'Maximum normalized solution error: ',worst_x
   print '(a,es12.4)', 'Maximum normalized prescribed-residual error: ',worst_r
   print '(a,es12.4)', 'Maximum normalized normal-equation residual: ',worst_s
   print '(a,i0)', 'Forlab real storage bits: ',storage_size(0.0_real64)
   print '(a)', 'PASS forlab-least-squares-reference'
contains
   subroutine orthogonal_factor(q,variant)
      real(real64),intent(out)::q(:,:)
      integer,intent(in)::variant
      real(real64)::norm
      integer::i,j,n
      n=size(q,1); q=0
      do i=1,n
         q(i,i)=1
      end do
      if (variant==1) return
      norm=real(sum([(i*i,i=1,n)]),real64)
      do j=1,n
         do i=1,n
            q(i,j)=q(i,j)-2*real(i*j,real64)/norm
         end do
      end do
   end subroutine orthogonal_factor
end program main
