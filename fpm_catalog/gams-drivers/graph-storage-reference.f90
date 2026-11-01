! Independent MIT consumer; see licenses/storage-ten-drivers-MIT.txt.
program main
   implicit none
   integer :: n
   do n=3,14
      call fixture(n)
   end do
   print '(a)', '12 dense undirected graphs; every adjacency index, degree, feature and edge weight'
   print '(a)', 'PASS graph-storage-reference'
contains
   subroutine fixture(n)
      use graphstruc, only: graph_type
      integer,intent(in) :: n
      type(graph_type) :: graph
      integer :: oracle(n,n),degree(n),i,j,k
      real :: feature(2)
      oracle=0
      degree=0
      do i=1,n
         feature=[real(i),real(-i)/4]
         call graph%add_vertex(feature=feature,id=100+i)
         feature=0
      end do
      k=0
      do j=2,n
         do i=1,j-1
            if(mod(i+2*j,3)/=0) cycle
            k=k+1
            oracle(i,j)=k
            oracle(j,i)=k
            degree(i)=degree(i)+1
            degree(j)=degree(j)+1
            call graph%add_edge(index=[i,j],weight=real(3*i-j)/8)
            if(any(graph%edge(k)%index/=[i,j])) error stop 'Edge endpoints'
            if(graph%edge(k)%weight/=real(3*i-j)/8) error stop 'Edge weight'
            if(graph%num_edges/=k) error stop 'Edge count'
            if(any(graph%adjacency/=oracle)) error stop 'Incremental adjacency'
         end do
      end do
      if(graph%num_vertices/=n) error stop 'Vertex count'
      do i=1,n
         if(graph%vertex(i)%degree/=degree(i)) error stop 'Degree oracle'
         if(graph%vertex(i)%id/=100+i) error stop 'Vertex identity'
         if(any(graph%vertex(i)%feature/=[real(i),real(-i)/4])) error stop 'Owned features'
      end do
   end subroutine
end program
