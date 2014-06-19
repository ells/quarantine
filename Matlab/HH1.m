function [ output_args ] = HH1( input_args )

%Havel-Hakimi Algorithm v1

n = size(degree_sequence,2);
% Check if the given degree sequence is graphical
degree_sequence_feasible = 1;
if mod(sum(degree_sequence),2)
    degree_sequence_feasible = 0;
else
    sorted_degree_sequence = sort(degree_sequence,'descend');
    for k=1:n
        temp_sum = 0;
        for i=k+1:n
            temp_sum = temp_sum + min(sorted_degree_sequence(i),k);
        end
        if (sum( sorted_degree_sequence(1:k)) > k*(k-1) + temp_sum )
            degree_sequence_feasible = 0;
        end
    end
end

m = sum(degree_sequence)/2;
E = zeros(m,2);

% Construct an initial graph with Havel-Hakini 
if degree_sequence_feasible
    ds = degree_sequence;
    i = 0;
    while sum(ds) > 0
        [residual_degree vertices] = sort(ds,'descend');
        selected_vertices = vertices(2:residual_degree(1)+1);
        E(i+1:i+residual_degree(1),:) = ...
            [repmat(vertices(1),residual_degree(1)) selected_vertices']; 
        i = i + residual_degree(1);
        ds(vertices(1)) = ds(vertices(1)) - residual_degree(1);
        ds(selected_vertices) = ds(selected_vertices) - 1;
    end
end

