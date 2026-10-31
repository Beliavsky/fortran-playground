! Independent API consumer; MIT: licenses/graph-neighbors-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use m_KdTree,only:KdTree,KdTreeSearch
   implicit none
   integer,parameter::sizes(*)=[1,2,8,31,64]
   type(KdTree)::tree
   type(KdTreeSearch)::search
   real(wp),allocatable::coordinates(:,:),saved(:,:)
   real(wp)::query(3),saved_query(3),distance,best,error,worst
   integer::dimensions,is,n,pattern,ordering,i,j,k,index,trees,calls,self_queries
   trees=0; calls=0; self_queries=0; worst=0
   do dimensions=2,3
      do is=1,size(sizes)
         n=sizes(is)
         allocate(coordinates(n,3),saved(n,3))
         do pattern=1,3
            do ordering=1,2
               do i=1,n
                  j=i
                  if (pattern==3) j=(i+1)/2
                  coordinates(i,:)=[real(mod(7*j,101),wp)/101,real(mod(13*j,103),wp)/103, &
                     real(mod(17*j,107),wp)/107]
                  if (pattern==2) coordinates(i,:)=[real(i-1,wp)/max(1,n-1),0.0_wp,0.0_wp]
               end do
               if (ordering==2) coordinates=coordinates(n:1:-1,:)
               saved=coordinates
               if (dimensions==2) then
                  tree=KdTree(coordinates(:,1),coordinates(:,2))
               else
                  tree=KdTree(coordinates(:,1),coordinates(:,2),coordinates(:,3))
               end if
               if (any(coordinates/=saved)) error stop 'constructor changed coordinates'
               do j=1,20+n
                  if (j<=20) then
                     query=[real(mod(11*j,31)-5,wp)/17,real(mod(7*j,29)-4,wp)/13, &
                        real(mod(13*j,37)-6,wp)/19]
                  else
                     query=coordinates(j-20,:)
                     self_queries=self_queries+1
                  end if
                  saved_query=query
                  best=huge(1.0_wp)
                  do i=1,n
                     distance=0
                     do k=1,dimensions
                        distance=distance+(coordinates(i,k)-query(k))**2
                     end do
                     best=min(best,distance)
                  end do
                  if (dimensions==2) then
                     index=search%nearest(tree,coordinates(:,1),coordinates(:,2),query(1),query(2))
                  else
                     index=search%nearest(tree,coordinates(:,1),coordinates(:,2),coordinates(:,3), &
                        query(1),query(2),query(3))
                  end if
                  if (index<1.or.index>n) error stop 'nearest index range'
                  distance=0
                  do k=1,dimensions
                     distance=distance+(coordinates(index,k)-query(k))**2
                  end do
                  if (.not.ieee_is_finite(distance)) error stop 'nonfinite nearest distance'
                  error=abs(distance-best)/max(1.0_wp,best)
                  if (error>5e-14_wp) then
                     print *, 'dimension,size,pattern,ordering,query:',dimensions,n,pattern,ordering,j
                     print *, 'returned/best squared distances:',distance,best
                     error stop 'direct nearest reference'
                  end if
                  if (j>20.and.distance/=0) error stop 'exact self query'
                  if (any(coordinates/=saved).or.any(query/=saved_query)) error stop 'changed search input'
                  worst=max(worst,error); calls=calls+1
               end do
               call tree%deallocate()
               trees=trees+1
            end do
         end do
         deallocate(coordinates,saved)
      end do
   end do
   if (trees/=60.or.calls/=2472.or.self_queries/=1272) error stop 'accounting'
   print '(a,i0,a,i0)', 'Two-/three-dimensional trees: ',trees,'; nearest queries: ',calls
   print '(a,i0)', 'Exact self queries, allowing duplicate-coordinate indices: ',self_queries
   print '(a)', 'Modular/collinear/duplicate-pair data; reversed ordering; repeated search state.'
   print '(a,es12.4)', 'Maximum normalized squared-distance error: ',worst
   print '(a)', 'PASS coretran-nearest-reference'
end program
