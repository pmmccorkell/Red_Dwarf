% # Patrick McCorkell
% # May 2022
% # US Naval Academy
% # Robotics and Control TSD
% #

classdef confInterval < matlab.mixin.SetGet
    properties(GetAccess='public', SetAccess='public')
        data_set
        alpha
        mn
        std_dev
        std_err
        tscore
        conf_interval
        conf_interval_range
    end % properties end

    methods(Access='public')
        function obj=confInterval(varargin)
            if nargin >= 1
                obj.data_set = varargin{1};
            else
                obj.data_set = rand(500,1);
            end
            if nargin >= 2
                obj.alpha = varargin{2};
            else
                obj.alpha = 0.95;
            end
            obj.calculate()
        end % init end

        function calculate(obj)
            obj.mn = mean(obj.data_set);
            obj.std_dev = std(obj.data_set);
            obj.std_err = obj.std_dev / (sqrt(length(obj.data_set)));
            obj.tscore = tinv([1-obj.alpha obj.alpha],length(obj.data_set)-1);
            obj.conf_interval = obj.mn + (obj.tscore * obj.std_err);
            obj.conf_interval_range = obj.conf_interval(2) - obj.conf_interval(1);
        end % calculate end

    end % methods end
end % class end
