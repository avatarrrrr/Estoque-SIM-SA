function erase() {
    if(confirm("Essa treta é realmente necessária?")){
      var request
      if(XMLHttpRequest){
        request = new XMLHttpRequest()
        request.onreadystatechange = function(){
          if(request.readyState === 4){
            if(request.status === 200){
              location = "/estoque"
            }
          }
        }
        request.open("DELETE", "/delete", true)
        request.send("{{produto[0]}}")
      }
    }
}