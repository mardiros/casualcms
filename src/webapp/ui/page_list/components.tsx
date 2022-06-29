import React from "react";
import { Box, Heading, Table, TableContainer, Tbody, Td, Th, Thead, Tr } from "@chakra-ui/react";
import { PartialPage } from "../../casualcms/domain/model";
import { ApiError } from "../../casualcms/domain/ports";
import { AppContext } from "../../config";

import { useAuth } from "../login/components";
import { Link, Navigate } from "react-router-dom";
export const PageList: React.FunctionComponent<{}> = () => {
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  const [pages, setPages] = React.useState<PartialPage[]>([]);
  const [error, setError] = React.useState<ApiError>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);

  React.useEffect(() => {
    async function loadRoots() {
      const rootPages = await config.api.page.listRoots(token);
      rootPages.
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
        pages.length &&
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
                            <Link to={`/admin/page/edit/root${page.slug}`}>Edit</Link>
                          </Td>
                          <Td>
                            <a href={`${page.slug}`}>View</a>
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
