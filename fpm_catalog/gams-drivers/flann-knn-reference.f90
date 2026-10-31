! Independent checked API consumer; see licenses/neighbors-sparse-drivers-MIT.txt.
program checked_flann_knn
   use iso_c_binding, only: c_float, c_int
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use flann, only: flann_index, KDTreeSingleIndexParams, search_params
   implicit none
   integer, parameter :: sizes(5)=[1,2,8,31,64]
   integer :: d,s,pattern,order,trees=0,queries=0,searches=0,neighbors=0
   do d=2,3
      do s=1,size(sizes)
         do pattern=1,3
            do order=1,2
               call fixture(d,sizes(s),pattern,order)
            end do
         end do
      end do
   end do
   print '(a,i0)', 'Trees: ',trees
   print '(a,i0)', 'Query points: ',queries
   print '(a,i0)', 'Batched exact searches: ',searches
   print '(a,i0)', 'Checked returned neighbors: ',neighbors
   print '(a)', 'PASS flann-knn-reference'
contains
   subroutine fixture(d,n,pattern,order)
      integer, intent(in) :: d,n,pattern,order
      real(c_float), target :: points(d,n)
      real(c_float) :: original(d,n),q(d,20+n),qcopy(d,20+n)
      real(real64) :: direct(n),sorted(n),value,tol,actual
      real(c_float), allocatable :: dist(:,:)
      integer(c_int), allocatable :: idx(:,:)
      integer(c_int) :: status
      integer :: i,j,l,t,h,k,ks(3),source
      do i=1,n
         source=i
         if (order==2) source=n+1-i
         if (pattern==3) source=(source+1)/2
         do j=1,d
            if (pattern==2) then
               points(j,i)=real(j*source,c_float)/32
            else
               points(j,i)=real(mod((6*j+1)*source,99+2*j),c_float)/real(99+2*j,c_float)
            end if
         end do
      end do
      original=points
      do i=1,20
         do j=1,d
            q(j,i)=real(mod((15-4*j)*i,33-2*j)-6+j,c_float)/real(21-4*j,c_float)
         end do
      end do
      q(:,21:)=points
      qcopy=q
      ks=[1,min(3,n),n]
      ! Block finalization frees the native index while points still exists.
      block
         type(flann_index) :: tree
         tree=flann_index(points,KDTreeSingleIndexParams(),'Euclidean')
         call tree%build_index()
         do t=1,3
            k=ks(t)
            allocate(idx(k,20+n),dist(k,20+n))
            idx=-1; dist=-1
            call tree%knn_search(q,idx,dist,int(k,c_int),search_params(checks=-1),stat=status)
            if (status/=0) error stop 'search status'
            if (.not.all(ieee_is_finite(dist))) error stop 'nonfinite distance'
            if (any(points/=original).or.any(q/=qcopy)) error stop 'input changed'
            do i=1,20+n
               do j=1,n
                  direct(j)=sum((real(original(:,j),real64)-real(q(:,i),real64))**2)
               end do
               sorted=direct
               ! Independent insertion sorting of direct-scan squared distances.
               do j=2,n
                  value=sorted(j); h=j-1
                  do while (h>=1)
                     if (sorted(h)<=value) exit
                     sorted(h+1)=sorted(h); h=h-1
                  end do
                  sorted(h+1)=value
               end do
               do j=1,k
                  l=idx(j,i)+1 ! FLANN indices are zero based.
                  if (l<1.or.l>n) error stop 'index range'
                  if (any(idx(:j-1,i)==idx(j,i))) error stop 'duplicate returned index'
                  actual=real(dist(j,i),real64)
                  tol=32*real(epsilon(1.0_c_float),real64)*max(1.0_real64,sorted(j))
                  if (abs(actual-direct(l))>tol) error stop 'distance/index mismatch'
                  if (abs(direct(l)-sorted(j))>tol) error stop 'not a kth nearest neighbor'
                  neighbors=neighbors+1
               end do
            end do
            deallocate(idx,dist)
            searches=searches+1
         end do
      end block
      trees=trees+1; queries=queries+20+n
   end subroutine fixture
end program checked_flann_knn
