## Autocarrier Loading Optimization under various loading policies
Three policies are proposed for loading optimization. Those are briefly discussed below. For more details, please see Kirtonia, et al. (2023). <br/>
**Policy 1a**: Exact solution approach for loading optimization. This is very computationally expensive and time-consuming. At each location, all possible loading states are generated, states between two locations are connected, and the state transition cost for each link is calculated.<br/>
**Policy 1b**: Heuristic solution approach. At each location, new loading states are generated based on the loading states at the previous locations. Certain rules prevent creating all possible loading states. This helps reduce the computation time by calculating the state transition cost for a smaller number of links.<br/>
**Policy 1c**: Heuristic solution approach that is significantly fast. More strict rules are applied for generating new loading states based on the previous states. Therefore, the solution quality is slightly compromized compared to Policy 1b which makes it significantly fast.

## Source code files
**LoadingOptimizationPolicy1a.py, LoadingOptimizationPolicy1b.py LoadingOptimizationPolicy1a.py**: Solve loading optimization problem under various loading policies.<br/>
**CheckStateFeasility.py**: Checks if a state is feasible or not given the loading state and loading constraints. <br/>
**SampleData.py**: Sample data to use for loading optimization.<br/>
**Jupyter notebook files**: Example steps for using the sample data, running loading optimization under various policies, showing results and drawing space state network.<br/>

## Comparison of space state networks
The following figure compares the space state network of Policy 1b and Policy 1c compared to Policy 1a. Policy 1a has all possible loading states and links since it's a brute-force exact solution approach. In policy 1b, some of the nodes are not present and the corresponding links are not there which makes it faster to solve. In policy 1c, only a few nodes and links are present. Although the solution quality is slightly worse than Policy 1b, this significantly improves the solution time.
<p align="center">
    <img src='figures/spaceStateNetPolicy 4 slot Combined.svg' width='650'>
</p>
<p align="center">
    Figure 1: Loading state representation
</p>

## References 
Kirtonia, S. K., Sun, Y., & Chen, Z. L. (2023). Selection of auto-carrier loading policy in automobile shipping. IISE Transactions, 1-20.
