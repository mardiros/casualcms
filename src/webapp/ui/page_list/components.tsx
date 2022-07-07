import React from "react";
import { Box, Heading, Icon, Table, TableContainer, Tbody, Td, Th, Thead, Tr } from "@chakra-ui/react";
import { PartialPage } from "../../casualcms/domain/model";
import { ApiError } from "../../casualcms/domain/ports";
import { AppContext } from "../../config";

import { useAuth } from "../login/components";
import { Link, Navigate, useParams } from "react-router-dom";
import { AddIcon, ChevronRightIcon, EditIcon, ViewIcon } from "@chakra-ui/icons";
import { Result, ResultAsync } from "neverthrow";

type PageListProps = {
  root?: boolean
}

export const PageList: React.FunctionComponent<PageListProps> = (props: PageListProps) => {
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const isRoot = props.root || false;
  const token = auth.authenticatedUser?.token || "";
  const [pages, setPages] = React.useState<PartialPage[]>([]);
  const [error, setError] = React.useState<ApiError>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const { parentPath } = useParams();

  React.useEffect(() => {
    async function loadRoots() {
      let pages: Result<PartialPage[], ApiError>;
      if (isRoot) {
        pages = await config.api.page.listRoots(token);

      }
      else {
        pages = await config.api.page.listPages(token, parentPath as string);
      }
      pages.
        map((pages: PartialPage[]) => setPages(pages)).
        mapErr((err: ApiError) => setError(err));
      setIsLoading(false);
    }
    loadRoots();
    return function cleanup() { };
  }, []);


  if (isLoading) {
    return <>Loading...</>
  }

  return (
    <Box>
      {
        !error &&
        <>
          <Heading>
            Pages
          </Heading>

          <Box paddingLeft={15}>
            <TableContainer>
              <Table variant='simple'>
                <Thead>
                  <Tr>
                    <Th>Page</Th>
                    <Th>Edit</Th>
                    <Th>View</Th>
                    <Th>Childs</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {
                    pages.map(
                      (page, i) =>
                        <Tr key={i}>
                          <Td>{page.title}</Td>
                          <Td>
                            <Link to={`/admin/page/edit/root${page.path}`}>
                              <Icon as={EditIcon} marginEnd={2}/>
                              Edit
                            </Link>
                          </Td>
                          <Td>
                            <a href={`${page.path}`}>
                              <Icon as={ViewIcon} marginEnd={2}/>
                              View
                            </a>
                          </Td>
                          <Td>
                            <a href="#">
                              <Icon as={AddIcon} marginEnd={2} />
                            </a>
                          </Td>
                        </Tr>
                    )}
                </Tbody>
              </Table>
            </TableContainer>
          </Box>
        </>
      }
      {/* TODO display error properly, just in cases */}
      {
        error &&
        <ul>
          {
            [...error.keys()].map((k) => <li> {error.get(k)} </li>)
          }
        </ul>
      }
    </Box>
  );
}
