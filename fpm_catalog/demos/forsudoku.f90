program solve_sudoku
   use sudoku, only: solve_puzzle
   implicit none
   integer :: grid(9,9), given(9,9), i,j,k,values(9)
   ! Each column here represents one displayed row of the puzzle.
   grid(:,1) = [5,3,0,0,7,0,0,0,0]
   grid(:,2) = [6,0,0,1,9,5,0,0,0]
   grid(:,3) = [0,9,8,0,0,0,0,6,0]
   grid(:,4) = [8,0,0,0,6,0,0,0,3]
   grid(:,5) = [4,0,0,8,0,3,0,0,1]
   grid(:,6) = [7,0,0,0,2,0,0,0,6]
   grid(:,7) = [0,6,0,0,0,0,2,8,0]
   grid(:,8) = [0,0,0,4,1,9,0,0,5]
   grid(:,9) = [0,0,0,0,8,0,0,7,9]
   given = grid
   call solve_puzzle(grid)
   if (any(grid<1) .or. any(grid>9)) error stop 'Incomplete solution'
   if (any(grid/=given .and. given/=0)) error stop 'Changed a given digit'
   do i=1,9
      do k=1,9
         if (count(grid(:,i)==k)/=1 .or. count(grid(i,:)==k)/=1) error stop 'Row or column check'
      end do
   end do
   do j=1,9,3
      do i=1,9,3
         values = reshape(grid(i:i+2,j:j+2),[9])
         do k=1,9
            if (count(values==k)/=1) error stop 'Block check'
         end do
      end do
   end do
   print '(a)', 'Solved Sudoku (rows, columns, blocks and original clues verified):'
   do j=1,9
      print '(3(3i2,2x))', grid(:,j)
   end do
   print *, 'PASS forsudoku'
end program
