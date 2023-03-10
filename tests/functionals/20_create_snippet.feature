Feature: As a user, I can create and publish snippets

  Scenario: Create a header snippet
    Given user on the admin page
    And a "/home" draft page of type "blog:HomePage"
    And a "/home/cat" draft page of type "blog:CategoryPage"
    And a "/home/dog" draft page of type "blog:CategoryPage"
    When I visit "/admin/snippets/new"
    Then I see the text "Choose A Type Of Snippet"
    And I see the text "Header Snippet"
    And I see the text "Footer Snippet"
    When I click on the "Header Snippet" link
    And I fill the field "key" with "header"
    And I fill the field "title" with "Casual Blog"
    # First link
    And I click on the "Add Item" button
    And I fill the "second" field "title" with "Cat"
    And I fill the field "href" with "/home/cat"
    # Second link
    And I click on the "Add Item" button
    And I fill the "third" field "title" with "Dog"
    And I fill the "second" field "href" with "/home/dog"
    # Submit the form
    And I click on the "Create Snippet" button
    Then I see the text "Header Snippet"
    And I see the text "header"
    And I see the text "Edit"
    When I visit "/admin/pages/preview?page=%2Fhome"
    Then I see the text "Casual Blog"
    And I see the text "Cat"
    And I see the text "Dog"
