program demo_graphstruc
   use graphstruc, only: graph_type
   implicit none
   type(graph_type) :: graph
   integer :: i

   graph%directed = .false.
   do i=1,4
      call graph%add_vertex(feature=[real(i)])
   end do
   call graph%add_edge(index=[1,2], weight=1.0)
   call graph%add_edge(index=[2,3], weight=1.0)
   call graph%add_edge(index=[3,4], weight=1.0)
   if (graph%num_vertices /= 4 .or. graph%num_edges /= 3) error stop 'Wrong graph size'
   if (any([(graph%vertex(i)%degree,i=1,4)] /= [1,2,2,1])) error stop 'Wrong degrees'
   if (any(graph%adjacency /= transpose(graph%adjacency))) error stop 'Graph is not symmetric'
   if (count(graph%adjacency /= 0) /= 6) error stop 'Wrong adjacency entries'
   do i=1,3
      if (graph%adjacency(i,i+1) == 0) error stop 'Missing edge'
   end do
   print '(a)', 'Undirected path: 1 -- 2 -- 3 -- 4'
   print '(a)', 'Adjacency matrix (edge indices; zero means no edge):'
   do i=1,4
      print '(4i4)', graph%adjacency(i,:)
   end do
   print '(a,4i3)', 'Vertex degrees:',(graph%vertex(i)%degree,i=1,4)
   print '(a)', 'PASS graphstruc'
end program
