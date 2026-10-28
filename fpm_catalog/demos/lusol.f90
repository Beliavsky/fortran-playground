! Factor a sparse matrix once, replace one column, and update the LU factors.
program demo_lusol
   use lusol, only: lu1fac,lu6sol,lu8rpc
   use lusol_precision, only: ip,wp=>rp
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer(ip), parameter :: n=4, capacity=10000
   integer(ip) :: indc(capacity),indr(capacity),p(n),q(n),lenc(n),lenr(n),locc(n),locr(n)
   integer(ip) :: iploc(n),iqloc(n),ipinv(n),iqinv(n),luparm(30),status,i,j,k
   real(wp) :: a(capacity),parmlu(30),work(n),v(n),x(n),dense(n,n),exact(n),rhs(n),diag,vnorm
   a=0; indc=0; indr=0
   dense=0
   do i=1,n
      dense(i,i)=4
      if (i<n) then
         dense(i,i+1)=-1
         dense(i+1,i)=-1
      end if
   end do
   k=0
   do j=1,n
      do i=1,n
         if (dense(i,j)==0) cycle
         k=k+1; indc(k)=i; indr(k)=j; a(k)=dense(i,j)
      end do
   end do
   ! Parameter initialization follows the upstream lusol_ez wrapper.
   luparm=0
   luparm(1)=6; luparm(3)=5; luparm(8)=1
   parmlu=0
   parmlu(1:8)=[100._wp,10._wp,epsilon(1._wp)**0.8_wp, &
      epsilon(1._wp)**0.67_wp,epsilon(1._wp)**0.67_wp,3._wp,0.3_wp,0.5_wp]
   call lu1fac(n,n,k,capacity,luparm,parmlu,a,indc,indr,p,q,lenc,lenr,locc,locr, &
      iploc,iqloc,ipinv,iqinv,work,status)
   if (status/=0) error stop 'LU factorization failed'
   exact=[1._wp,-2._wp,3._wp,-4._wp]
   call check_solution('Original system')
   dense(:,2)=[0.5_wp,5._wp,-0.5_wp,0.25_wp]
   v=dense(:,2)
   call lu8rpc(1_ip,1_ip,n,n,2_ip,v,work,capacity,luparm,parmlu,a,indc,indr,p,q, &
      lenc,lenr,locc,locr,status,diag,vnorm)
   if (status/=0) error stop 'Column update failed'
   call check_solution('After replacing column 2')
   print '(a)', 'PASS lusol'
contains
   subroutine check_solution(label)
      character(*),intent(in) :: label
      real(wp) :: err,residual
      rhs=matmul(dense,exact)
      v=rhs
      call lu6sol(5_ip,n,n,v,x,capacity,luparm,parmlu,a,indc,indr,p,q,lenc,lenr,locc,locr,status)
      if (status/=0) error stop 'LU solve failed'
      if (.not.all(ieee_is_finite(x))) error stop 'Nonfinite solution'
      err=maxval(abs(x-exact)); residual=maxval(abs(matmul(dense,x)-rhs))
      print '(a)', label
      print '(a,4f12.7)', 'Solution: ',x
      print '(a,2es14.3)', 'Solution error and residual: ',err,residual
      if (max(err,residual)>1e-11_wp) error stop 'LU solution inaccurate'
   end subroutine
end program
