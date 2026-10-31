! Independent API consumer; see licenses/propack-fmm-drivers-MIT.txt.
module checked_propack_operator
   use iso_fortran_env, only: real64
   implicit none
   real(real64), allocatable :: matrix(:,:)
contains
   subroutine product(trans,m,n,x,y,dparm,iparm)
      character :: trans
      integer :: m,n,iparm(*)
      real(real64) :: x(*),y(*),dparm(*)
      integer :: i,j
      select case(trans)
      case('n','N')
         y(1:m)=0
         do j=1,n
            do i=1,m
               y(i)=y(i)+matrix(i,j)*x(j)
            end do
         end do
         iparm(1)=iparm(1)+1
      case('t','T')
         y(1:n)=0
         do j=1,n
            do i=1,m
               y(j)=y(j)+matrix(i,j)*x(i)
            end do
         end do
         iparm(2)=iparm(2)+1
      case default
         error stop 'unsupported operator transpose'
      end select
   end subroutine product
end module checked_propack_operator
program checked_propack
   use checked_propack_operator
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   interface
      subroutine dlansvd(jobu,jobv,m,n,k,kmax,aprod,u,ldu,sigma,bnd,v,ldv,tolin, &
                         work,lwork,iwork,liwork,doption,ioption,info,dparm,iparm)
         import real64
         character :: jobu,jobv
         integer :: m,n,k,kmax,ldu,ldv,lwork,liwork,info,iwork(liwork),ioption(*),iparm(*)
         real(real64) :: u(ldu,*),v(ldv,*),sigma(*),bnd(*),tolin,work(lwork),doption(*),dparm(*)
         external :: aprod
      end subroutine dlansvd
   end interface
   integer, parameter :: sizes(3)=[8,12,20]
   integer :: s,shape,rotation,scale,request,solves=0,triplets=0
   real(real64) :: worst_sigma=0,worst_residual=0,worst_orthogonality=0
   do s=1,3
      do shape=-3,3,3
         do rotation=0,1
            do scale=1,3
               do request=1,3,2
                  call fixture(sizes(s)+shape,sizes(s),rotation,scale,request)
               end do
            end do
         end do
      end do
   end do
   print '(a,i0)', 'Partial SVD calls: ',solves
   print '(a,i0)', 'Checked leading triplets: ',triplets
   print '(a,es12.4)', 'Maximum operator-scaled singular-value error: ',worst_sigma
   print '(a,es12.4)', 'Maximum operator-scaled triplet residual: ',worst_residual
   print '(a,es12.4)', 'Maximum orthogonality error: ',worst_orthogonality
   print '(a)', 'PASS propack-spectrum-reference'
contains
   subroutine fixture(m,n,rotation,scale,wanted)
      integer, intent(in) :: m,n,rotation,scale,wanted
      integer, parameter :: lwork=100000,liwork=2000
      integer :: rank,k,info,i,j,l,r,iwork(liwork),ioptions(2),iparm(2)
      real(real64) :: saved(m,n),amplitude,anorm,angle,c,s,error,value,residual,orthogonality
      real(real64) :: row1(n),row2(n),col1(m),col2(m),av(m),atu(n),options(3),dparm(1),tolerance
      real(real64), allocatable :: u(:,:),v(:,:),sigma(:),bounds(:),work(:)
      rank=min(m,n); amplitude=8.0_real64**(scale-2); anorm=rank*amplitude
      allocate(matrix(m,n),u(m,rank+1),v(n,rank),sigma(rank),bounds(rank),work(lwork))
      matrix=0
      do i=1,rank
         matrix(i,i)=amplitude*(rank-i+1)
      end do
      if (rotation==1) then
         do i=1,m-1
            angle=0.17_real64+0.01_real64*i; c=cos(angle); s=sin(angle)
            row1=matrix(i,:); row2=matrix(i+1,:)
            matrix(i,:)=c*row1-s*row2; matrix(i+1,:)=s*row1+c*row2
         end do
         do j=1,n-1
            angle=0.31_real64+0.007_real64*j; c=cos(angle); s=sin(angle)
            col1=matrix(:,j); col2=matrix(:,j+1)
            matrix(:,j)=c*col1-s*col2; matrix(:,j+1)=s*col1+c*col2
         end do
      end if
      saved=matrix
      u=0; v=0; sigma=0; bounds=0; work=0; iwork=0; iparm=0; dparm=0
      u(:,1)=sum(matrix,dim=2) ! Deterministic, nonzero start in the column space.
      options=[-1.0_real64,-1.0_real64,anorm]; ioptions=[1,1]; tolerance=1e-12_real64; k=wanted
      call dlansvd('Y','Y',m,n,k,rank,product,u,m,sigma,bounds,v,n,tolerance, &
         work,lwork,iwork,liwork,options,ioptions,info,dparm,iparm)
      if (info/=0.or.k/=wanted) error stop 'partial SVD convergence/count'
      if (any(iparm<1)) error stop 'both operator directions were not used'
      if (any(matrix/=saved)) error stop 'operator matrix changed'
      if (.not.all(ieee_is_finite(sigma(:k))).or..not.all(ieee_is_finite(bounds(:k)))) &
         error stop 'nonfinite singular values/bounds'
      if (.not.all(ieee_is_finite(u(:,:k))).or..not.all(ieee_is_finite(v(:,:k)))) &
         error stop 'nonfinite singular vectors'
      if (any(bounds(:k)<0)) error stop 'negative singular-value bound'
      do j=1,k
         error=abs(sigma(j)-amplitude*(rank-j+1))/anorm
         worst_sigma=max(worst_sigma,error)
         if (error>2e-9_real64) error stop 'known leading singular value mismatch'
         ! Independent scalar residuals; do not reuse the APROD callback as the oracle.
         av=0; atu=0
         do l=1,n
            do r=1,m
               av(r)=av(r)+saved(r,l)*v(l,j)
               atu(l)=atu(l)+saved(r,l)*u(r,j)
            end do
         end do
         residual=max(norm2(av-sigma(j)*u(:,j)),norm2(atu-sigma(j)*v(:,j)))/anorm
         worst_residual=max(worst_residual,residual)
         if (residual>2e-9_real64) error stop 'singular triplet residual'
         do i=1,k
            value=real(merge(1,0,i==j),real64)
            orthogonality=max(abs(sum(u(:,i)*u(:,j))-value),abs(sum(v(:,i)*v(:,j))-value))
            worst_orthogonality=max(worst_orthogonality,orthogonality)
            if (orthogonality>2e-9_real64) error stop 'singular vector orthogonality'
         end do
      end do
      triplets=triplets+k; solves=solves+1
      deallocate(matrix)
   end subroutine fixture
end program checked_propack
