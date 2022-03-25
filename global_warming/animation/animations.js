
        const zeroPad = (num, places) => String(num).padStart(places, '0')

        function create_new_g(idx, plot_kind, color, country, to_hide = 0) {
       
            var newG = document.createElementNS("http://www.w3.org/2000/svg", 'g'); 
            newG.setAttribute("clip-path","url('#_clipPath_frame_"+zeroPad(idx,3)+"')"); 
            newG.setAttribute("style", "display:block;");

            if ( to_hide === 1){
                newG.setAttribute("id", "to_hide");
            }

            var newImage = document.createElementNS("http://www.w3.org/2000/svg", 'image'); 
            newImage.setAttribute("x","0");     
            newImage.setAttribute("y","0");     
            newImage.setAttribute("width","800");     
            newImage.setAttribute("height","800");     
            newImage.setAttribute("href","../../output/"+plot_kind+"/"+country+"/"+color+"/plot_"+color+"_frame_"+zeroPad(idx,3)+".svg");     
            
            newG.appendChild(newImage);  

            return newG

        }

        function build_svg_frames(nbr_images, plot_kind,  color, country){

            var svg = document.getElementById('main_svg'); //Get svg element
            
            for (let i = 1; i < nbr_images; i++) { 
                console.log(i)
                newG = create_new_g(i, plot_kind,  color, country)
                svg.appendChild(newG)
            }
           
            newG = create_new_g(0, plot_kind, color, country, 1)
            svg.appendChild(newG)

        }
