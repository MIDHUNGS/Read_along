

rendition.on('rendered', function(location){
  index=location['index']
  var urlParams = new URLSearchParams(window.location.search);
  name_of_book=urlParams.get('book').replace(/ /g,"_")
  // console.log(location['contents'].getElementsByTagName('p').item('0').innerHTML)
    // index=location.start.index;
    // this.index=index;
    //console.log(index)
    if(index>=4){
      document.getElementById('passage-audio').style.display='block'
      document.getElementsByClassName('playback-rate')[0].style.visibility='visible'
      document.getElementsByClassName('autofocus-current-word')[0].style.visibility='visible'
      document.getElementById('passage-text').style.display='block'
      page=index-3

  filen='sentence'+String(page)
  // console.log(filen)

  fetch('/audio/'+String(name_of_book)+'/Text/'+filen+'.txt')
.then(response => response.text())
.then(data => {
  // Do something with your data

  //changing values of inner html of epub
//   epub_inner=location['contents'].getElementsByTagName('p')
 
//   for(i=0;i<epub_inner.length;i++){
// epub_inner.item(String(i)).innerHTML=''
//   }
//   epub_inner.item('0').innerHTML=data
document.getElementById("passage-text").innerHTML=data
      
});

fetch('/audio/'+String(name_of_book)+'/Test/'+filen+'.wav')
.then(response => response.text())
.then(data => {
  
  var myAudio = document.getElementById('passage-audio');
  myAudio.setAttribute('src',data);
  });

    }
   
else{
  document.getElementById('passage-audio').style.display='none'
  document.getElementsByClassName('playback-rate')[0].style.visibility='hidden'
  document.getElementsByClassName('autofocus-current-word')[0].style.visibility='hidden'
  document.getElementById('passage-text').style.display='none'
  
  fetch('/audio/All_About_Eggs/hello.txt')
.then(response => response.text())
.then(data => {
  // Do something with your data
  
document.getElementById("passage-text").innerHTML=data

});

fetch('/audio/All_About_Eggs/Test/sentence2.wav')
.then(response => response.text())
.then(data => {

var myAudio = document.getElementById('passage-audio');
myAudio.setAttribute('src',data);
});


}

});


  


      
    