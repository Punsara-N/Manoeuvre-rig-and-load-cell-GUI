%% Parses experiment data files using python script 'recparse.py'

function parse(fileList)

%     filePath = 'C:\FIWT\fiwt-master\FIWT-APC';
%     filePath = 'C:\GitHub\Manoeuvre-rig-and-load-cell-GUI';
% 
%     cd(filePath);

    for i = 1:length(fileList)
        
        fprintf(['Parsing exp ' int2str(fileList(i)) '...']);
        
        try
            filename = dir([filePath '\FIWT_Exp' int2str(fileList(i)) '*']);
            if isempty(filename)
                fprintf(' SKIPPED');
                fprintf('\n');
                continue;
            end
        catch
            
        end
        
        try
            command = ['python recparse.py FIWT_Exp' int2str(fileList(i)) '*.dat'];
            system(command);
            fprintf(' DONE');
            fprintf('\n');
        catch e
            fprintf(' FAILED');
            fprintf('\n');
            fprintf(1,'The identifier was:\n%s',e.identifier);
            fprintf(1,'There was an error! The message was:\n%s',e.message);
            fprintf('\n');
        end

    end
    
%     cd('C:\FIWT\workspace');