document.getElementById('radio-orig').checked = true;
document.getElementById('radio-self').checked = false;

function clickOriginals(e) {
    document.getElementsByClassName('ans-orig')[0].style.display = 'flex';
    document.getElementsByClassName('ans-self')[0].style.display = 'none';
    // Profile 페이지에서 my bookmarks 있는 경우에만
    if (document.getElementsByClassName('ans-orig')[1]) {
        document.getElementsByClassName('ans-orig')[1].style.display = 'flex';
    } else {}
    if (document.getElementsByClassName('ans-self')[1]) {
        document.getElementsByClassName('ans-self')[1].style.display = 'none';
    } else{}
    
    document.getElementById('radio-orig-text').style.color = 'black';
    document.getElementById('radio-orig-text').style.fontWeight = '800';
    document.getElementById('radio-self-text').style.color = 'grey';
    document.getElementById('radio-self-text').style.fontWeight = '400';

    document.getElementById('ques_type_desc').innerText = '하루에 하나씩 제공되는 질문이에요'
}

function clickSelf(e) {
    document.getElementsByClassName('ans-orig')[0].style.display = 'none';
    document.getElementsByClassName('ans-self')[0].style.display = 'flex';
    // Profile 페이지에서 my bookmarks 있는 경우에만
    if (document.getElementsByClassName('ans-orig')[1]) {
        document.getElementsByClassName('ans-orig')[1].style.display = 'none';
    } else {}
    if (document.getElementsByClassName('ans-self')[1]) {
        document.getElementsByClassName('ans-self')[1].style.display = 'flex';
    } else{}

    document.getElementById('radio-orig-text').style.color = 'grey';
    document.getElementById('radio-orig-text').style.fontWeight = '400';
    document.getElementById('radio-self-text').style.color = 'black';
    document.getElementById('radio-self-text').style.fontWeight = '800';

    document.getElementById('ques_type_desc').innerText = '내가 스스로 고민한 질문과 정답이에요'
}   

/*
window.onload = function radioBtn() {
    console.log('radio button function called')
    // Radiobutton 초기화
    document.getElementById('radio-orig').checked = true;
    document.getElementById('radio-self').checked = false;

    var btnOriginals = document.getElementById('radio-orig')
    var btnSelf = document.getElementById('radio-self')
    
    btnOriginals.addEventListener('click', clickOriginals);
    btnSelf.addEventListener('click', clickSelf);

    function clickOriginals(e) {
        document.getElementsByClassName('ans-orig')[0].style.display = 'flex';
        document.getElementsByClassName('ans-self')[0].style.display = 'none';
        // Profile 페이지에서 my bookmarks 있는 경우에만
        if (document.getElementsByClassName('ans-orig')[1]) {
            document.getElementsByClassName('ans-orig')[1].style.display = 'flex';
        } else {}
        if (document.getElementsByClassName('ans-self')[1]) {
            document.getElementsByClassName('ans-self')[1].style.display = 'none';
        } else{}
        
        document.getElementById('radio-orig-text').style.color = 'black';
        document.getElementById('radio-orig-text').style.fontWeight = '800';
        document.getElementById('radio-self-text').style.color = 'grey';
        document.getElementById('radio-self-text').style.fontWeight = '400';

        document.getElementById('ques_type_desc').innerText = '하루에 하나씩 제공되는 질문이에요'
    }
    
    function clickSelf(e) {
        document.getElementsByClassName('ans-orig')[0].style.display = 'none';
        document.getElementsByClassName('ans-self')[0].style.display = 'flex';
        // Profile 페이지에서 my bookmarks 있는 경우에만
        if (document.getElementsByClassName('ans-orig')[1]) {
            document.getElementsByClassName('ans-orig')[1].style.display = 'none';
        } else {}
        if (document.getElementsByClassName('ans-self')[1]) {
            document.getElementsByClassName('ans-self')[1].style.display = 'flex';
        } else{}

        document.getElementById('radio-orig-text').style.color = 'grey';
        document.getElementById('radio-orig-text').style.fontWeight = '400';
        document.getElementById('radio-self-text').style.color = 'black';
        document.getElementById('radio-self-text').style.fontWeight = '800';

        document.getElementById('ques_type_desc').innerText = '내가 스스로 고민한 질문과 정답이에요'
    }   
}
*/

