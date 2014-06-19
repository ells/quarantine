function [ output_args ] = HH2( input_args )

%Havel-Hakimi algorithm v2

sort_seq = sort(seq, 'descend');
disp(sort_seq);
 
    if (sum(sort_seq) &gt; 0)
       firstvalue = sort_seq(1);
 
    if firstvalue &gt;= max(size(sort_seq))
          disp('Not graphical');
    end
 
       newseq = sort_seq(:, 2:(max(size(sort_seq))));
 
       for i = 1:firstvalue;
            newseq(i) = newseq(i) - 1;
       end
 
       HavelHakimi(newseq);
    elseif (sum(abs(sort_seq)) == 0)
        disp('Graphical');
    else
        disp('Not graphical');
    end
return

end

